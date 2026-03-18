use anyhow::Result;
use evdev::{AbsoluteAxisCode, Device, EventSummary, KeyCode, RelativeAxisCode};
use mister_fpga::core::file::SdCard;
use mister_fpga::core::MisterFpgaCore;
use mister_fpga::keyboard::Ps2Scancode;
use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};
use tracing::{debug, info, warn};

use crate::analog::{self, AnalogState};
use crate::button_remap::{self, ButtonRemap};
use crate::hotkey::{self, HotkeyAction};
use crate::keyboard_map;
use crate::osd;
use crate::savestate;
use crate::sd_emu;

/// Maximum number of player gamepad slots.
const MAX_GAMEPADS: usize = 6;

/// Poll interval for the input loop (~1ms).
const POLL_INTERVAL: Duration = Duration::from_millis(1);

/// How often to check for newly connected devices.
const HOTPLUG_INTERVAL: Duration = Duration::from_secs(5);

/// Deadzone threshold as a fraction of the axis range (25%).
const ANALOG_DEADZONE_FRAC: f32 = 0.25;

/// Analog trigger threshold: >50% of range = pressed.
const TRIGGER_THRESHOLD_FRAC: f32 = 0.50;

/// Mouse movement threshold (pixels) to register as a direction press.
const MOUSE_MOVE_THRESHOLD: i32 = 2;

/// Per-axis calibration info captured at enumeration time.
#[derive(Clone, Copy)]
struct AxisInfo {
    minimum: i32,
    maximum: i32,
}

impl AxisInfo {
    fn center(&self) -> i32 {
        (self.minimum + self.maximum) / 2
    }

    fn half_range(&self) -> f32 {
        ((self.maximum - self.minimum) as f32) / 2.0
    }

    fn is_positive(&self, value: i32) -> bool {
        let offset = (value - self.center()) as f32;
        offset > self.half_range() * ANALOG_DEADZONE_FRAC
    }

    fn is_negative(&self, value: i32) -> bool {
        let offset = (value - self.center()) as f32;
        offset < -(self.half_range() * ANALOG_DEADZONE_FRAC)
    }

    fn trigger_pressed(&self, value: i32) -> bool {
        let range = (self.maximum - self.minimum) as f32;
        let normalized = (value - self.minimum) as f32 / range;
        normalized > TRIGGER_THRESHOLD_FRAC
    }
}

/// A tracked gamepad device assigned to a player slot.
struct GamepadSlot {
    path: PathBuf,
    device: Device,
    left_stick: Option<(AxisInfo, AxisInfo)>,
    right_stick: Option<(AxisInfo, AxisInfo)>,
    triggers: Option<(AxisInfo, AxisInfo)>,
    analog: AnalogState,
}

/// A tracked keyboard device.
struct KeyboardSlot {
    path: PathBuf,
    device: Device,
}

/// A tracked mouse device.
struct MouseSlot {
    path: PathBuf,
    device: Device,
}

/// Parameters for save state operations in the input loop.
pub struct SaveContext {
    pub save_dir: PathBuf,
    pub system: String,
    pub rom: PathBuf,
}

/// Context for multi-disc swapping in the input loop.
pub struct DiscContext {
    /// All disc image paths in playlist order.
    pub disc_paths: Vec<PathBuf>,
    /// Mount slot index used for the disc (e.g. 0 for CD systems).
    pub mount_index: u8,
    /// Current disc index in the playlist.
    current_disc: usize,
}

impl DiscContext {
    pub fn new(disc_paths: Vec<PathBuf>, mount_index: u8) -> Self {
        Self {
            disc_paths,
            mount_index,
            current_disc: 0,
        }
    }
}

/// Run the main input loop. Blocks until the exit hotkey is triggered.
///
/// `system` is used for per-system button remapping. If None, the default
/// generic mapping is used.
pub fn run_input_loop(
    core: &mut MisterFpgaCore,
    save_ctx: Option<&SaveContext>,
    mut disc_ctx: Option<&mut DiscContext>,
    system: Option<&str>,
    screenshots_dir: Option<&Path>,
) -> Result<()> {
    let remap = system.map_or_else(
        || button_remap::get_remap(""),
        button_remap::get_remap,
    );

    let mut gamepads = enumerate_gamepads()?;
    let mut keyboards = enumerate_keyboards()?;
    let mut mice = enumerate_mice()?;
    let mut hotkey_tracker = hotkey::HotkeyTracker::new();
    let mut status_osd = osd::StatusOsd::new();
    let mut last_hotplug_check = Instant::now();
    let mut osd_active = false;

    info!(
        "Input loop started with {} gamepad(s), {} keyboard(s), {} mouse/mice",
        gamepads.len().min(MAX_GAMEPADS),
        keyboards.len(),
        mice.len()
    );

    loop {
        // Hot-plug: periodically check for new devices
        if last_hotplug_check.elapsed() >= HOTPLUG_INTERVAL {
            hotplug_check(&mut gamepads, &mut keyboards, &mut mice);
            last_hotplug_check = Instant::now();
        }

        // Process evdev events from all gamepads
        let mut disconnected_pads: Vec<usize> = Vec::new();
        for (player_idx, slot) in gamepads.iter_mut().enumerate() {
            if player_idx >= MAX_GAMEPADS {
                break;
            }
            match process_gamepad_events(core, slot, player_idx as u8, &mut hotkey_tracker, &remap, osd_active)
            {
                Ok(()) => {}
                Err(e) => {
                    // ENODEV means the device was disconnected
                    if is_device_gone(&e) {
                        info!("Gamepad {} disconnected", slot.path.display());
                        disconnected_pads.push(player_idx);
                    } else {
                        debug!("Gamepad {player_idx} event error: {e:#}");
                    }
                }
            }
        }
        // Remove disconnected gamepads (in reverse order to preserve indices)
        for idx in disconnected_pads.into_iter().rev() {
            gamepads.remove(idx);
        }

        // Process keyboard events
        keyboards.retain_mut(|kb| {
            match process_keyboard_events(core, kb) {
                Err(e) if is_device_gone(&e) => {
                    info!("Keyboard disconnected: {}", kb.path.display());
                    false
                }
                Err(e) => {
                    debug!("Keyboard event error: {e:#}");
                    true
                }
                Ok(()) => true,
            }
        });

        // Process mouse events
        mice.retain_mut(|mouse| {
            match process_mouse_events(core, mouse) {
                Err(e) if is_device_gone(&e) => {
                    info!("Mouse disconnected: {}", mouse.path.display());
                    false
                }
                Err(e) => {
                    debug!("Mouse event error: {e:#}");
                    true
                }
                Ok(()) => true,
            }
        });

        // Poll SD card emulation
        if let Err(e) = sd_emu::poll_sd(core) {
            debug!("SD poll error: {e:#}");
        }

        // Check hotkey actions
        match hotkey_tracker.poll_action() {
            HotkeyAction::Exit => {
                info!("Exit hotkey detected");
                break;
            }
            HotkeyAction::SaveState(slot) => {
                if let Some(ctx) = save_ctx {
                    let path =
                        savestate::save_path(&ctx.save_dir, &ctx.system, &ctx.rom, slot);
                    match savestate::save_slot(core, slot, &path) {
                        Ok(true) => {
                            info!("Saved state slot {slot}");
                            status_osd.show(core, &format!("SAVED SLOT {slot}"));
                        }
                        Ok(false) => debug!("Save state slot {slot} skipped"),
                        Err(e) => warn!("Save state slot {slot} failed: {e:#}"),
                    }
                }
            }
            HotkeyAction::LoadState(slot) => {
                if let Some(ctx) = save_ctx {
                    let path =
                        savestate::save_path(&ctx.save_dir, &ctx.system, &ctx.rom, slot);
                    match savestate::load_slot(core, slot, &path) {
                        Ok(true) => {
                            info!("Loaded state slot {slot}");
                            status_osd.show(core, &format!("LOADED SLOT {slot}"));
                        }
                        Ok(false) => debug!("Load state slot {slot} skipped"),
                        Err(e) => warn!("Load state slot {slot} failed: {e:#}"),
                    }
                }
            }
            HotkeyAction::SlotChanged(slot) => {
                info!("Save slot changed to {slot}");
                status_osd.show(core, &format!("SLOT {slot}"));
            }
            HotkeyAction::SoftReset => {
                info!("Soft reset triggered");
                core.soft_reset();
                status_osd.show(core, "RESET");
            }
            HotkeyAction::ToggleOsd => {
                osd_active = !osd_active;
                info!("OSD {} (F12)", if osd_active { "opened" } else { "closed" });
                core.key_down(Ps2Scancode::F12);
                core.key_up(Ps2Scancode::F12);
            }
            HotkeyAction::NextDisc => {
                if let Some(ref mut dctx) = disc_ctx {
                    swap_disc(core, dctx, true, &mut status_osd, system);
                }
            }
            HotkeyAction::PrevDisc => {
                if let Some(ref mut dctx) = disc_ctx {
                    swap_disc(core, dctx, false, &mut status_osd, system);
                }
            }
            HotkeyAction::Screenshot => {
                if let Some(dir) = screenshots_dir {
                    take_screenshot(core, dir, &mut status_osd);
                }
            }
            HotkeyAction::None => {}
        }

        // Auto-hide OSD after timeout
        status_osd.tick(core);

        std::thread::sleep(POLL_INTERVAL);
    }

    Ok(())
}

/// Check if an error indicates the device was disconnected.
fn is_device_gone(e: &anyhow::Error) -> bool {
    if let Some(io_err) = e.downcast_ref::<std::io::Error>() {
        matches!(io_err.raw_os_error(), Some(19)) // ENODEV
    } else {
        false
    }
}

/// Check for newly connected devices and add them to the slot lists.
fn hotplug_check(
    gamepads: &mut Vec<GamepadSlot>,
    keyboards: &mut Vec<KeyboardSlot>,
    mice: &mut Vec<MouseSlot>,
) {
    let known_paths: HashSet<PathBuf> = gamepads
        .iter()
        .map(|s| s.path.clone())
        .chain(keyboards.iter().map(|s| s.path.clone()))
        .chain(mice.iter().map(|s| s.path.clone()))
        .collect();

    for (path, device) in evdev::enumerate() {
        if known_paths.contains(&path) {
            continue;
        }

        // Try to classify as gamepad
        if gamepads.len() < MAX_GAMEPADS {
            let has_abs = device.supported_absolute_axes().map_or(false, |axes| {
                axes.contains(AbsoluteAxisCode::ABS_X)
                    || axes.contains(AbsoluteAxisCode::ABS_HAT0X)
            });
            let has_gamepad_buttons = device.supported_keys().map_or(false, |keys| {
                keys.contains(KeyCode::BTN_SOUTH) || keys.contains(KeyCode::BTN_SELECT)
            });

            if has_abs || has_gamepad_buttons {
                info!(
                    "Hot-plug: gamepad connected: {} (player {})",
                    device.name().unwrap_or("unknown"),
                    gamepads.len()
                );
                let left_stick =
                    query_axis_pair(&device, AbsoluteAxisCode::ABS_X, AbsoluteAxisCode::ABS_Y);
                let right_stick =
                    query_axis_pair(&device, AbsoluteAxisCode::ABS_RX, AbsoluteAxisCode::ABS_RY);
                let triggers =
                    query_axis_pair(&device, AbsoluteAxisCode::ABS_Z, AbsoluteAxisCode::ABS_RZ);
                gamepads.push(GamepadSlot {
                    path,
                    device,
                    left_stick,
                    right_stick,
                    triggers,
                    analog: AnalogState::default(),
                });
                continue;
            }
        }

        // Try mouse (before keyboard since some devices match both)
        let has_rel = device.supported_relative_axes().map_or(false, |axes| {
            axes.contains(RelativeAxisCode::REL_X) && axes.contains(RelativeAxisCode::REL_Y)
        });
        let has_mouse_btn = device
            .supported_keys()
            .map_or(false, |keys| keys.contains(KeyCode::BTN_LEFT));
        let is_gamepad = device
            .supported_keys()
            .map_or(false, |keys| keys.contains(KeyCode::BTN_SOUTH));

        if has_rel && has_mouse_btn && !is_gamepad {
            info!(
                "Hot-plug: mouse connected: {}",
                device.name().unwrap_or("unknown")
            );
            mice.push(MouseSlot { path, device });
            continue;
        }

        // Try keyboard
        let is_keyboard = device.supported_keys().map_or(false, |keys| {
            keys.contains(KeyCode::KEY_A) && keys.contains(KeyCode::KEY_ENTER)
        });
        if is_keyboard {
            info!(
                "Hot-plug: keyboard connected: {}",
                device.name().unwrap_or("unknown")
            );
            keyboards.push(KeyboardSlot { path, device });
        }
    }
}

/// Enumerate evdev devices and assign gamepads to player slots.
fn enumerate_gamepads() -> Result<Vec<GamepadSlot>> {
    let mut slots = Vec::new();

    for (path, device) in evdev::enumerate() {
        let has_abs = device.supported_absolute_axes().map_or(false, |axes| {
            axes.contains(AbsoluteAxisCode::ABS_X)
                || axes.contains(AbsoluteAxisCode::ABS_HAT0X)
        });

        let has_gamepad_buttons = device.supported_keys().map_or(false, |keys| {
            keys.contains(KeyCode::BTN_SOUTH) || keys.contains(KeyCode::BTN_SELECT)
        });

        if has_abs || has_gamepad_buttons {
            info!(
                "Found gamepad: {} (player {})",
                device.name().unwrap_or("unknown"),
                slots.len()
            );

            let left_stick =
                query_axis_pair(&device, AbsoluteAxisCode::ABS_X, AbsoluteAxisCode::ABS_Y);
            let right_stick =
                query_axis_pair(&device, AbsoluteAxisCode::ABS_RX, AbsoluteAxisCode::ABS_RY);
            let triggers =
                query_axis_pair(&device, AbsoluteAxisCode::ABS_Z, AbsoluteAxisCode::ABS_RZ);

            slots.push(GamepadSlot {
                path,
                device,
                left_stick,
                right_stick,
                triggers,
                analog: AnalogState::default(),
            });
            if slots.len() >= MAX_GAMEPADS {
                break;
            }
        }
    }

    if slots.is_empty() {
        warn!("No gamepads found");
    }

    Ok(slots)
}

/// Query AbsInfo for a pair of axes.
fn query_axis_pair(
    device: &Device,
    axis_a: AbsoluteAxisCode,
    axis_b: AbsoluteAxisCode,
) -> Option<(AxisInfo, AxisInfo)> {
    let absinfo = device.get_absinfo().ok()?;
    let mut a_info = None;
    let mut b_info = None;
    for (axis, info) in absinfo {
        if axis == axis_a {
            a_info = Some(AxisInfo {
                minimum: info.minimum(),
                maximum: info.maximum(),
            });
        } else if axis == axis_b {
            b_info = Some(AxisInfo {
                minimum: info.minimum(),
                maximum: info.maximum(),
            });
        }
    }
    Some((a_info?, b_info?))
}

/// Enumerate keyboard devices.
fn enumerate_keyboards() -> Result<Vec<KeyboardSlot>> {
    let mut slots = Vec::new();

    for (path, device) in evdev::enumerate() {
        let is_keyboard = device.supported_keys().map_or(false, |keys| {
            keys.contains(KeyCode::KEY_A) && keys.contains(KeyCode::KEY_ENTER)
        });

        if is_keyboard {
            info!("Found keyboard: {}", device.name().unwrap_or("unknown"));
            slots.push(KeyboardSlot { path, device });
        }
    }

    Ok(slots)
}

/// Enumerate mouse devices.
fn enumerate_mice() -> Result<Vec<MouseSlot>> {
    let mut slots = Vec::new();

    for (path, device) in evdev::enumerate() {
        let has_rel = device.supported_relative_axes().map_or(false, |axes| {
            axes.contains(RelativeAxisCode::REL_X) && axes.contains(RelativeAxisCode::REL_Y)
        });
        let has_mouse_btn = device
            .supported_keys()
            .map_or(false, |keys| keys.contains(KeyCode::BTN_LEFT));
        let is_gamepad = device
            .supported_keys()
            .map_or(false, |keys| keys.contains(KeyCode::BTN_SOUTH));

        if has_rel && has_mouse_btn && !is_gamepad {
            info!("Found mouse: {}", device.name().unwrap_or("unknown"));
            slots.push(MouseSlot { path, device });
        }
    }

    Ok(slots)
}

/// Process pending evdev events for a single gamepad and forward to the FPGA core.
///
/// When `osd_active` is true, D-pad/buttons are redirected as PS/2 keyboard
/// scancodes for OSD menu navigation instead of gamepad button presses.
fn process_gamepad_events(
    core: &mut MisterFpgaCore,
    slot: &mut GamepadSlot,
    player_idx: u8,
    hotkey_tracker: &mut hotkey::HotkeyTracker,
    remap: &ButtonRemap,
    osd_active: bool,
) -> Result<()> {
    let events = match slot.device.fetch_events() {
        Ok(events) => events,
        Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => return Ok(()),
        Err(e) => return Err(e.into()),
    };

    for event in events {
        match event.destructure() {
            EventSummary::Key(_ev, code, value) => {
                let pressed = value != 0;
                // Hotkey tracker always uses raw evdev codes (not remapped)
                hotkey_tracker.update_key(code, pressed);

                if osd_active {
                    // OSD mode: redirect specific buttons to keyboard scancodes
                    osd_handle_button(core, code, pressed);
                } else {
                    // Normal mode: send gamepad buttons
                    if let Some(button_idx) = button_remap::map_button(remap, code) {
                        if pressed {
                            core.gamepad_button_down(player_idx, button_idx);
                        } else {
                            core.gamepad_button_up(player_idx, button_idx);
                        }
                    }
                }
            }

            EventSummary::AbsoluteAxis(_ev, axis, value) => {
                if osd_active {
                    // OSD mode: D-pad/stick → arrow keys
                    osd_handle_axis(core, &slot.left_stick, axis, value);
                    // Still update hotkey tracker for hat D-pad
                    if axis == AbsoluteAxisCode::ABS_HAT0Y {
                        hotkey_tracker.update_hat(true, value);
                    }
                } else {
                    // Normal mode
                    match axis {
                        // D-pad hat switch
                        AbsoluteAxisCode::ABS_HAT0X => {
                            core.gamepad_button_up(player_idx, MISTER_RIGHT);
                            core.gamepad_button_up(player_idx, MISTER_LEFT);
                            if value > 0 {
                                core.gamepad_button_down(player_idx, MISTER_RIGHT);
                            } else if value < 0 {
                                core.gamepad_button_down(player_idx, MISTER_LEFT);
                            }
                        }
                        AbsoluteAxisCode::ABS_HAT0Y => {
                            core.gamepad_button_up(player_idx, MISTER_DOWN);
                            core.gamepad_button_up(player_idx, MISTER_UP);
                            if value > 0 {
                                core.gamepad_button_down(player_idx, MISTER_DOWN);
                            } else if value < 0 {
                                core.gamepad_button_down(player_idx, MISTER_UP);
                            }
                            hotkey_tracker.update_hat(true, value);
                        }

                        // Left analog stick → digital D-pad + analog output
                        AbsoluteAxisCode::ABS_X => {
                            if let Some((x_info, _)) = &slot.left_stick {
                                // Digital D-pad conversion
                                core.gamepad_button_up(player_idx, MISTER_RIGHT);
                                core.gamepad_button_up(player_idx, MISTER_LEFT);
                                if x_info.is_positive(value) {
                                    core.gamepad_button_down(player_idx, MISTER_RIGHT);
                                } else if x_info.is_negative(value) {
                                    core.gamepad_button_down(player_idx, MISTER_LEFT);
                                }
                                // Analog output
                                slot.analog.left_x =
                                    analog::axis_to_i8(value, x_info.minimum, x_info.maximum);
                                analog::send_analog(core, player_idx, &slot.analog);
                            }
                        }
                        AbsoluteAxisCode::ABS_Y => {
                            if let Some((_, y_info)) = &slot.left_stick {
                                // Digital D-pad conversion
                                core.gamepad_button_up(player_idx, MISTER_DOWN);
                                core.gamepad_button_up(player_idx, MISTER_UP);
                                if y_info.is_positive(value) {
                                    core.gamepad_button_down(player_idx, MISTER_DOWN);
                                } else if y_info.is_negative(value) {
                                    core.gamepad_button_down(player_idx, MISTER_UP);
                                }
                                // Analog output
                                slot.analog.left_y =
                                    analog::axis_to_i8(value, y_info.minimum, y_info.maximum);
                                analog::send_analog(core, player_idx, &slot.analog);
                            }
                        }

                        // Right analog stick → digital directions + analog output
                        AbsoluteAxisCode::ABS_RX => {
                            if let Some((rx_info, _)) = &slot.right_stick {
                                core.gamepad_button_up(player_idx, MISTER_MS_RIGHT);
                                core.gamepad_button_up(player_idx, MISTER_MS_LEFT);
                                if rx_info.is_positive(value) {
                                    core.gamepad_button_down(player_idx, MISTER_MS_RIGHT);
                                } else if rx_info.is_negative(value) {
                                    core.gamepad_button_down(player_idx, MISTER_MS_LEFT);
                                }
                                // Analog output
                                slot.analog.right_x =
                                    analog::axis_to_i8(value, rx_info.minimum, rx_info.maximum);
                                analog::send_analog(core, player_idx, &slot.analog);
                            }
                        }
                        AbsoluteAxisCode::ABS_RY => {
                            if let Some((_, ry_info)) = &slot.right_stick {
                                core.gamepad_button_up(player_idx, MISTER_MS_DOWN);
                                core.gamepad_button_up(player_idx, MISTER_MS_UP);
                                if ry_info.is_positive(value) {
                                    core.gamepad_button_down(player_idx, MISTER_MS_DOWN);
                                } else if ry_info.is_negative(value) {
                                    core.gamepad_button_down(player_idx, MISTER_MS_UP);
                                }
                                // Analog output
                                slot.analog.right_y =
                                    analog::axis_to_i8(value, ry_info.minimum, ry_info.maximum);
                                analog::send_analog(core, player_idx, &slot.analog);
                            }
                        }

                        // Analog triggers → digital L2/R2 (uses remap indices)
                        AbsoluteAxisCode::ABS_Z => {
                            if let Some((z_info, _)) = &slot.triggers {
                                if z_info.trigger_pressed(value) {
                                    core.gamepad_button_down(player_idx, remap.tl2);
                                } else {
                                    core.gamepad_button_up(player_idx, remap.tl2);
                                }
                            }
                        }
                        AbsoluteAxisCode::ABS_RZ => {
                            if let Some((_, rz_info)) = &slot.triggers {
                                if rz_info.trigger_pressed(value) {
                                    core.gamepad_button_down(player_idx, remap.tr2);
                                } else {
                                    core.gamepad_button_up(player_idx, remap.tr2);
                                }
                            }
                        }

                        _ => {}
                    }
                }
            }

            _ => {}
        }
    }

    Ok(())
}

/// When OSD is active, map gamepad buttons to PS/2 keyboard scancodes for menu navigation.
fn osd_handle_button(core: &mut MisterFpgaCore, code: KeyCode, pressed: bool) {
    let scancode = match code {
        KeyCode::BTN_SOUTH => Some(Ps2Scancode::Enter),
        KeyCode::BTN_EAST => Some(Ps2Scancode::Esc),
        KeyCode::BTN_DPAD_UP => Some(Ps2Scancode::Up),
        KeyCode::BTN_DPAD_DOWN => Some(Ps2Scancode::Down),
        KeyCode::BTN_DPAD_LEFT => Some(Ps2Scancode::Left),
        KeyCode::BTN_DPAD_RIGHT => Some(Ps2Scancode::Right),
        _ => None,
    };
    if let Some(sc) = scancode {
        if pressed {
            core.key_down(sc);
        } else {
            core.key_up(sc);
        }
    }
}

/// When OSD is active, map D-pad hat and analog stick to PS/2 arrow key scancodes.
fn osd_handle_axis(
    core: &mut MisterFpgaCore,
    left_stick: &Option<(AxisInfo, AxisInfo)>,
    axis: AbsoluteAxisCode,
    value: i32,
) {
    match axis {
        AbsoluteAxisCode::ABS_HAT0X => {
            core.key_up(Ps2Scancode::Right);
            core.key_up(Ps2Scancode::Left);
            if value > 0 {
                core.key_down(Ps2Scancode::Right);
            } else if value < 0 {
                core.key_down(Ps2Scancode::Left);
            }
        }
        AbsoluteAxisCode::ABS_HAT0Y => {
            core.key_up(Ps2Scancode::Down);
            core.key_up(Ps2Scancode::Up);
            if value > 0 {
                core.key_down(Ps2Scancode::Down);
            } else if value < 0 {
                core.key_down(Ps2Scancode::Up);
            }
        }
        AbsoluteAxisCode::ABS_X => {
            if let Some((x_info, _)) = left_stick {
                core.key_up(Ps2Scancode::Right);
                core.key_up(Ps2Scancode::Left);
                if x_info.is_positive(value) {
                    core.key_down(Ps2Scancode::Right);
                } else if x_info.is_negative(value) {
                    core.key_down(Ps2Scancode::Left);
                }
            }
        }
        AbsoluteAxisCode::ABS_Y => {
            if let Some((_, y_info)) = left_stick {
                core.key_up(Ps2Scancode::Down);
                core.key_up(Ps2Scancode::Up);
                if y_info.is_positive(value) {
                    core.key_down(Ps2Scancode::Down);
                } else if y_info.is_negative(value) {
                    core.key_down(Ps2Scancode::Up);
                }
            }
        }
        _ => {}
    }
}

/// Process pending keyboard events and forward as PS/2 scancodes.
fn process_keyboard_events(core: &mut MisterFpgaCore, kb: &mut KeyboardSlot) -> Result<()> {
    let events = match kb.device.fetch_events() {
        Ok(events) => events,
        Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => return Ok(()),
        Err(e) => return Err(e.into()),
    };

    for event in events {
        if let EventSummary::Key(_ev, _code, value) = event.destructure() {
            let linux_code = event.code();
            if let Some(scancode) = keyboard_map::linux_key_to_ps2(linux_code) {
                if value != 0 {
                    core.key_down(scancode);
                } else {
                    core.key_up(scancode);
                }
            }
        }
    }

    Ok(())
}

/// Process pending mouse events and forward to FPGA core as mouse buttons/directions.
fn process_mouse_events(core: &mut MisterFpgaCore, mouse: &mut MouseSlot) -> Result<()> {
    let events = match mouse.device.fetch_events() {
        Ok(events) => events,
        Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => return Ok(()),
        Err(e) => return Err(e.into()),
    };

    let player: u8 = 0;

    for event in events {
        match event.destructure() {
            EventSummary::Key(_ev, code, value) => {
                let pressed = value != 0;
                if let Some(btn) = map_mouse_button(code) {
                    if pressed {
                        core.gamepad_button_down(player, btn);
                    } else {
                        core.gamepad_button_up(player, btn);
                    }
                }
            }
            EventSummary::RelativeAxis(_ev, axis, value) => match axis {
                RelativeAxisCode::REL_X => {
                    core.gamepad_button_up(player, MISTER_MS_RIGHT);
                    core.gamepad_button_up(player, MISTER_MS_LEFT);
                    if value > MOUSE_MOVE_THRESHOLD {
                        core.gamepad_button_down(player, MISTER_MS_RIGHT);
                    } else if value < -MOUSE_MOVE_THRESHOLD {
                        core.gamepad_button_down(player, MISTER_MS_LEFT);
                    }
                }
                RelativeAxisCode::REL_Y => {
                    core.gamepad_button_up(player, MISTER_MS_DOWN);
                    core.gamepad_button_up(player, MISTER_MS_UP);
                    if value > MOUSE_MOVE_THRESHOLD {
                        core.gamepad_button_down(player, MISTER_MS_DOWN);
                    } else if value < -MOUSE_MOVE_THRESHOLD {
                        core.gamepad_button_down(player, MISTER_MS_UP);
                    }
                }
                _ => {}
            },
            _ => {}
        }
    }

    Ok(())
}

// D-pad indices (always fixed regardless of remap)
const MISTER_RIGHT: u8 = 0;
const MISTER_LEFT: u8 = 1;
const MISTER_DOWN: u8 = 2;
const MISTER_UP: u8 = 3;

// Mouse direction buttons (indices 12-15 in MisterFpgaButtons)
const MISTER_MS_RIGHT: u8 = 12;
const MISTER_MS_LEFT: u8 = 13;
const MISTER_MS_DOWN: u8 = 14;
const MISTER_MS_UP: u8 = 15;

// Mouse click buttons
const MISTER_MS_BTN_L: u8 = 16;
const MISTER_MS_BTN_R: u8 = 17;
const MISTER_MS_BTN_M: u8 = 18;

/// Map a mouse button KeyCode to a MiSTer button index.
fn map_mouse_button(code: KeyCode) -> Option<u8> {
    match code {
        KeyCode::BTN_LEFT => Some(MISTER_MS_BTN_L),
        KeyCode::BTN_RIGHT => Some(MISTER_MS_BTN_R),
        KeyCode::BTN_MIDDLE => Some(MISTER_MS_BTN_M),
        _ => None,
    }
}

/// Swap to the next or previous disc in the playlist.
///
/// For PSX, toggles the CD lid status bit (bit 15) during swap.
fn swap_disc(
    core: &mut MisterFpgaCore,
    dctx: &mut DiscContext,
    forward: bool,
    status_osd: &mut osd::StatusOsd,
    system: Option<&str>,
) {
    let count = dctx.disc_paths.len();
    if count <= 1 {
        return;
    }

    let new_idx = if forward {
        (dctx.current_disc + 1) % count
    } else {
        (dctx.current_disc + count - 1) % count
    };

    let path = &dctx.disc_paths[new_idx];
    info!("Swapping to disc {} of {}: {}", new_idx + 1, count, path.display());

    // For PSX: open CD lid (status bit 15 = 1) before swap
    let is_psx = system == Some("psx");
    if is_psx {
        let mut bits = *core.status_bits();
        bits.set(15, true);
        core.send_status_bits(bits);
        debug!("PSX: CD lid opened");
    }

    // Mount the new disc
    match SdCard::from_path(path) {
        Ok(card) => {
            match core.mount(card, dctx.mount_index) {
                Ok(()) => {
                    dctx.current_disc = new_idx;
                    let msg = format!("DISC {}/{}", new_idx + 1, count);
                    status_osd.show(core, &msg);
                    info!("Disc swap complete: {}", path.display());
                }
                Err(e) => {
                    warn!("Failed to mount disc: {e}");
                    status_osd.show(core, "DISC ERR");
                }
            }
        }
        Err(e) => {
            warn!("Failed to open disc image {}: {e}", path.display());
            status_osd.show(core, "DISC ERR");
        }
    }

    // For PSX: close CD lid (status bit 15 = 0) after swap
    if is_psx {
        let mut bits = *core.status_bits();
        bits.set(15, false);
        core.send_status_bits(bits);
        debug!("PSX: CD lid closed");
    }
}

/// Take a screenshot from the FPGA framebuffer and save as PNG.
fn take_screenshot(
    core: &mut MisterFpgaCore,
    screenshots_dir: &Path,
    status_osd: &mut osd::StatusOsd,
) {
    use std::fs;

    if let Err(e) = fs::create_dir_all(screenshots_dir) {
        warn!("Cannot create screenshots dir: {e}");
        return;
    }

    // Generate timestamped filename
    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    let path = screenshots_dir.join(format!("screenshot_{timestamp}.png"));

    match core.take_screenshot() {
        Ok(img) => {
            if let Err(e) = img.save(&path) {
                warn!("Failed to save screenshot: {e}");
                status_osd.show(core, "SHOT ERR");
            } else {
                info!("Screenshot saved: {}", path.display());
                status_osd.show(core, "SCREENSHOT");
            }
        }
        Err(e) => {
            warn!("Screenshot capture failed: {e}");
            status_osd.show(core, "SHOT ERR");
        }
    }
}
