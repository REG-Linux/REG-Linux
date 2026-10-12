use evdev::KeyCode;
use std::time::{Duration, Instant};

/// How long Select+Start must be held to trigger exit.
const EXIT_HOLD_DURATION: Duration = Duration::from_secs(2);

/// Maximum save state slot index.
pub const MAX_SAVE_SLOT: usize = 3;

/// Actions triggered by hotkey combos.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HotkeyAction {
    None,
    Exit,
    /// Save to current slot.
    SaveState(usize),
    /// Load from current slot.
    LoadState(usize),
    /// Slot changed (for display feedback).
    SlotChanged(usize),
    /// Soft reset the core.
    SoftReset,
    /// Swap to the next disc (for multi-disc games).
    NextDisc,
    /// Swap to the previous disc.
    PrevDisc,
    /// Toggle the core's OSD menu (sends F12 to core).
    ToggleOsd,
    /// Take a screenshot.
    Screenshot,
}

/// Tracks hotkey button state and detects combos.
///
/// - Select + Start (2s hold)    → Exit
/// - Select + L1 (instant)       → SaveState(current_slot)
/// - Select + R1 (instant)       → LoadState(current_slot)
/// - Select + DPad Up (instant)  → next slot
/// - Select + DPad Down (instant)→ prev slot
/// - Select + X/North (instant)  → SoftReset
/// - Select + L2 (instant)       → PrevDisc
/// - Select + R2 (instant)       → NextDisc
/// - Select + Y/West (instant)   → ToggleOsd
/// - Select + B/East (instant)   → Screenshot
pub struct HotkeyTracker {
    select_pressed: bool,
    start_pressed: bool,
    l1_pressed: bool,
    r1_pressed: bool,
    l2_pressed: bool,
    r2_pressed: bool,
    x_pressed: bool,
    y_pressed: bool,
    b_pressed: bool,
    dpad_up_pressed: bool,
    dpad_down_pressed: bool,
    /// When Select+Start both became pressed, or None.
    both_pressed_since: Option<Instant>,
    /// Pending instant action to emit once.
    pending_action: Option<HotkeyAction>,
    /// Current save slot (0..=MAX_SAVE_SLOT).
    current_slot: usize,
}

impl HotkeyTracker {
    pub fn new() -> Self {
        Self {
            select_pressed: false,
            start_pressed: false,
            l1_pressed: false,
            r1_pressed: false,
            l2_pressed: false,
            r2_pressed: false,
            x_pressed: false,
            y_pressed: false,
            b_pressed: false,
            dpad_up_pressed: false,
            dpad_down_pressed: false,
            both_pressed_since: None,
            pending_action: None,
            current_slot: 0,
        }
    }

    /// Update state based on a key press/release event.
    pub fn update_key(&mut self, code: KeyCode, pressed: bool) {
        match code {
            KeyCode::BTN_SELECT => self.select_pressed = pressed,
            KeyCode::BTN_START => self.start_pressed = pressed,
            KeyCode::BTN_TL => {
                if pressed && !self.l1_pressed && self.select_pressed {
                    self.pending_action = Some(HotkeyAction::SaveState(self.current_slot));
                }
                self.l1_pressed = pressed;
            }
            KeyCode::BTN_TR => {
                if pressed && !self.r1_pressed && self.select_pressed {
                    self.pending_action = Some(HotkeyAction::LoadState(self.current_slot));
                }
                self.r1_pressed = pressed;
            }
            KeyCode::BTN_NORTH => {
                if pressed && !self.x_pressed && self.select_pressed {
                    self.pending_action = Some(HotkeyAction::SoftReset);
                }
                self.x_pressed = pressed;
            }
            KeyCode::BTN_WEST => {
                if pressed && !self.y_pressed && self.select_pressed {
                    self.pending_action = Some(HotkeyAction::ToggleOsd);
                }
                self.y_pressed = pressed;
            }
            KeyCode::BTN_EAST => {
                if pressed && !self.b_pressed && self.select_pressed {
                    self.pending_action = Some(HotkeyAction::Screenshot);
                }
                self.b_pressed = pressed;
            }
            KeyCode::BTN_TL2 => {
                if pressed && !self.l2_pressed && self.select_pressed {
                    self.pending_action = Some(HotkeyAction::PrevDisc);
                }
                self.l2_pressed = pressed;
            }
            KeyCode::BTN_TR2 => {
                if pressed && !self.r2_pressed && self.select_pressed {
                    self.pending_action = Some(HotkeyAction::NextDisc);
                }
                self.r2_pressed = pressed;
            }
            KeyCode::BTN_DPAD_UP => {
                if pressed && !self.dpad_up_pressed && self.select_pressed {
                    self.current_slot = (self.current_slot + 1).min(MAX_SAVE_SLOT);
                    self.pending_action = Some(HotkeyAction::SlotChanged(self.current_slot));
                }
                self.dpad_up_pressed = pressed;
            }
            KeyCode::BTN_DPAD_DOWN => {
                if pressed && !self.dpad_down_pressed && self.select_pressed {
                    self.current_slot = self.current_slot.saturating_sub(1);
                    self.pending_action = Some(HotkeyAction::SlotChanged(self.current_slot));
                }
                self.dpad_down_pressed = pressed;
            }
            _ => return,
        }

        // Track Select+Start hold for exit
        if self.select_pressed && self.start_pressed {
            if self.both_pressed_since.is_none() {
                self.both_pressed_since = Some(Instant::now());
            }
        } else {
            self.both_pressed_since = None;
        }
    }

    /// Update state from a hat/axis event (for D-pad on hat switch).
    pub fn update_hat(&mut self, is_y: bool, value: i32) {
        if !self.select_pressed {
            return;
        }
        if is_y {
            // HAT0Y: negative = up, positive = down
            if value < 0 && !self.dpad_up_pressed {
                self.current_slot = (self.current_slot + 1).min(MAX_SAVE_SLOT);
                self.pending_action = Some(HotkeyAction::SlotChanged(self.current_slot));
            } else if value > 0 && !self.dpad_down_pressed {
                self.current_slot = self.current_slot.saturating_sub(1);
                self.pending_action = Some(HotkeyAction::SlotChanged(self.current_slot));
            }
            self.dpad_up_pressed = value < 0;
            self.dpad_down_pressed = value > 0;
        }
    }

    /// Poll for the current hotkey action. Instant actions are consumed on read.
    pub fn poll_action(&mut self) -> HotkeyAction {
        // Check exit hold first
        if let Some(since) = self.both_pressed_since {
            if since.elapsed() >= EXIT_HOLD_DURATION {
                return HotkeyAction::Exit;
            }
        }

        // Consume any pending instant action
        self.pending_action.take().unwrap_or(HotkeyAction::None)
    }
}
