use anyhow::Result;
use mister_fpga::config::Config;
use mister_fpga::core::volume::Volume;
use mister_fpga::core::MisterFpgaCore;
use mister_fpga::fpga::user_io::{
    ButtonSwitches, EnableGamma, IsGammaSupported, SetCustomAspectRatio, UserIoButtonSwitch,
};
use std::path::Path;
use tracing::{info, warn};

/// Apply video and audio configuration to the FPGA core.
///
/// This re-sends button switches and volume after core initialization.
/// Call this before loading ROMs or entering the input loop.
///
/// If `config_path` is provided, settings are loaded from the INI file first
/// and CLI arguments override them.
pub fn apply_video_audio(
    core: &mut MisterFpgaCore,
    volume: u8,
    forced_scandoubler: bool,
    hdmi_audio_96k: bool,
    dvi: bool,
    hdmi_limited: u8,
    direct_video: bool,
    vga_scaler: bool,
    composite_sync: bool,
    ypbpr: bool,
    vga_sog: bool,
    brightness: u8,
    contrast: u8,
    config_path: Option<&Path>,
    custom_aspect_ratio: Option<&str>,
) -> Result<()> {
    // Load defaults from config file if provided
    let mut cfg_scandoubler = false;
    let mut cfg_audio_96k = false;
    let mut cfg_dvi = false;
    let mut cfg_limited: u8 = 0;
    let mut cfg_direct = false;
    let mut cfg_vga_scaler = false;
    let mut cfg_composite_sync = false;
    let mut cfg_ypbpr = false;
    let mut cfg_vga_sog = false;
    let mut cfg_brightness: u8 = 50;
    let mut cfg_contrast: u8 = 50;

    if let Some(path) = config_path {
        match Config::load(path) {
            Ok(config) => {
                let mc = config.into_inner();
                info!("Loaded config from: {}", path.display());
                cfg_scandoubler = mc.forced_scandoubler.unwrap_or(false);
                cfg_audio_96k = mc.hdmi_audio_96k.unwrap_or(false);
                cfg_dvi = mc.dvi_mode.unwrap_or(false);
                cfg_limited = match mc.hdmi_limited {
                    Some(mister_fpga::config::HdmiLimitedConfig::Limited) => 1,
                    Some(mister_fpga::config::HdmiLimitedConfig::LimitedForVgaConverters) => 2,
                    _ => 0,
                };
                cfg_direct = mc.direct_video.unwrap_or(false);
                cfg_vga_scaler = mc.vga_scaler.unwrap_or(false);
                cfg_composite_sync = false; // Not in config, button-only
                cfg_ypbpr = matches!(
                    mc.vga_mode,
                    Some(mister_fpga::config::VgaMode::Ypbpr)
                );
                cfg_vga_sog = mc.vga_sog.unwrap_or(false);
                cfg_brightness = ((mc.video_brightness() + 0.5) * 100.0) as u8;
                cfg_contrast = (((mc.video_contrast() - 1.0) / 2.0 + 0.5) * 100.0) as u8;
            }
            Err(e) => {
                warn!("Failed to load config {}: {e}", path.display());
            }
        }
    }

    // CLI flags override config file values (boolean flags: true wins)
    let eff_scandoubler = forced_scandoubler || cfg_scandoubler;
    let eff_audio_96k = hdmi_audio_96k || cfg_audio_96k;
    let eff_dvi = dvi || cfg_dvi;
    let eff_limited = if hdmi_limited > 0 { hdmi_limited } else { cfg_limited };
    let eff_direct = direct_video || cfg_direct;
    let eff_vga_scaler = vga_scaler || cfg_vga_scaler;
    let eff_composite_sync = composite_sync || cfg_composite_sync;
    let eff_ypbpr = ypbpr || cfg_ypbpr;
    let eff_vga_sog = vga_sog || cfg_vga_sog;
    let eff_brightness = if brightness != 50 { brightness } else { cfg_brightness };
    let eff_contrast = if contrast != 50 { contrast } else { cfg_contrast };

    // Apply volume (0-100 mapped to 0-255 scale)
    let vol_scaled = ((volume.min(100) as u16) * 255 / 100) as u8;
    core.send_volume(Volume::scaled(vol_scaled))
        .map_err(|e| anyhow::anyhow!("Failed to set volume: {e}"))?;
    if volume < 100 {
        info!("Volume set to {}%", volume);
    }

    // Build button switches for video/audio hardware configuration
    let mut switches = UserIoButtonSwitch::new();
    if eff_scandoubler {
        switches |= ButtonSwitches::ForcedScandoubler;
        info!("Forced scandoubler enabled");
    }
    if eff_audio_96k {
        switches |= ButtonSwitches::Audio96K;
        info!("HDMI audio: 96kHz/16bit");
    }
    if eff_dvi {
        switches |= ButtonSwitches::Dvi;
        info!("DVI mode (no HDMI audio)");
    }
    match eff_limited {
        1 => {
            switches |= ButtonSwitches::HdmiLimited1;
            info!("HDMI limited color range");
        }
        2 => {
            switches |= ButtonSwitches::HdmiLimited2;
            info!("HDMI limited color range (VGA converters)");
        }
        _ => {}
    }
    if eff_direct {
        switches |= ButtonSwitches::DirectVideo;
        info!("Direct video output enabled");
    }
    if eff_vga_scaler {
        switches |= ButtonSwitches::VgaScaler;
        info!("VGA scaler enabled");
    }
    if eff_composite_sync {
        switches |= ButtonSwitches::CompositeSync;
        info!("Composite sync enabled");
    }
    if eff_ypbpr {
        switches |= ButtonSwitches::Ypbpr;
        info!("YPbPr output enabled");
    }
    if eff_vga_sog {
        switches |= ButtonSwitches::VgaSog;
        info!("VGA sync on green enabled");
    }

    // Send button switches via SPI
    core.spi_mut()
        .execute(switches)
        .map_err(|e| anyhow::anyhow!("Failed to send video switches: {e}"))?;

    // Apply custom aspect ratio if specified (format: "H:V", e.g. "16:9", "4:3")
    if let Some(ar) = custom_aspect_ratio {
        if let Some((h, v)) = parse_aspect_ratio(ar) {
            core.spi_mut()
                .execute(SetCustomAspectRatio::new(h, v))
                .map_err(|e| anyhow::anyhow!("Failed to set aspect ratio: {e}"))?;
            info!("Custom aspect ratio: {h}:{v}");
        } else {
            warn!("Invalid aspect ratio format '{ar}', expected 'H:V' (e.g. '16:9')");
        }
    }

    // Apply gamma correction for brightness/contrast adjustment
    if eff_brightness != 50 || eff_contrast != 50 {
        apply_gamma(core, eff_brightness, eff_contrast)?;
    }

    Ok(())
}

/// Apply brightness and contrast via the FPGA gamma correction LUT.
///
/// Brightness: 0-100 (50=neutral), Contrast: 0-100 (50=neutral).
/// Builds a 256-entry per-channel gamma LUT and sends via SPI.
fn apply_gamma(core: &mut MisterFpgaCore, brightness: u8, contrast: u8) -> Result<()> {
    // Check if the core supports gamma correction
    let mut supported = false;
    core.spi_mut()
        .execute(IsGammaSupported(&mut supported))
        .map_err(|e| anyhow::anyhow!("Failed to query gamma support: {e}"))?;

    if !supported {
        info!("Core does not support gamma correction, skipping brightness/contrast");
        return Ok(());
    }

    // Convert to floating point ranges matching MisterConfig conventions:
    //   brightness: [-0.5..0.5] from [0..100]
    //   contrast: [0..2] from [0..100]
    let b = (brightness.clamp(0, 100) as f32 / 100.0) - 0.5;
    let c = ((contrast.clamp(0, 100) as f32 / 100.0) - 0.5) * 2.0 + 1.0;

    // Build 256-entry gamma LUT
    let mut lut: Vec<(u8, u8, u8)> = Vec::with_capacity(256);
    for i in 0..256u16 {
        let normalized = i as f32 / 255.0;
        // Apply contrast (scale around 0.5) then brightness (offset)
        let v = (normalized - 0.5) * c + 0.5 + b;
        let v = (v * 255.0).clamp(0.0, 255.0) as u8;
        lut.push((v, v, v));
    }

    core.spi_mut()
        .execute(EnableGamma(&lut))
        .map_err(|e| anyhow::anyhow!("Failed to set gamma: {e}"))?;

    info!("Gamma correction: brightness={brightness}, contrast={contrast}");
    Ok(())
}

/// Parse an aspect ratio string like "16:9" or "4:3" into (horizontal, vertical).
fn parse_aspect_ratio(s: &str) -> Option<(u16, u16)> {
    let (h_str, v_str) = s.split_once(':')?;
    let h: u16 = h_str.trim().parse().ok()?;
    let v: u16 = v_str.trim().parse().ok()?;
    if h > 0 && v > 0 {
        Some((h, v))
    } else {
        None
    }
}
