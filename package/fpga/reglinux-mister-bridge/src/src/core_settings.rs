use anyhow::{Context, Result};
use mister_fpga::config_string::ConfigMenu;
use mister_fpga::core::MisterFpgaCore;
use mister_fpga::types::StatusBitMap;
use tracing::{info, warn};

/// A parsed status bit setting: set bits `start..end` to `value`.
#[derive(Debug)]
pub struct BitSetting {
    pub start: u8,
    pub end: u8,
    pub value: u32,
}

/// Parse a setting string that may be named. Returns either a resolved BitSetting
/// or the raw key=value pair for named resolution.
///
/// Raw bit format:
///   "5:8=3"   → set bits 5..8 to value 3
///   "10=1"    → set bit 10 to value 1
///
/// Named format (resolved against core's config menu):
///   "Region=Japan"    → find the "Region" option and set to the "Japan" choice index
///   "Aspect Ratio=2"  → find the option and set to choice index 2
pub enum ParsedSetting {
    Raw(BitSetting),
    Named { key: String, value: String },
}

pub fn parse_setting_flexible(s: &str) -> Result<ParsedSetting> {
    let (key, value_str) = s
        .split_once('=')
        .context("Setting must be in format 'key=value'")?;

    let key = key.trim();
    let value_str = value_str.trim();

    if key.bytes().next().map_or(false, |b| b.is_ascii_digit()) {
        let value: u32 = value_str
            .parse()
            .with_context(|| format!("Invalid value: {value_str}"))?;

        if let Some((start_str, end_str)) = key.split_once(':') {
            let start: u8 = start_str.trim().parse()?;
            let end: u8 = end_str.trim().parse()?;
            anyhow::ensure!(start < end && end <= 128);
            Ok(ParsedSetting::Raw(BitSetting { start, end, value }))
        } else {
            let bit: u8 = key.parse()?;
            anyhow::ensure!(bit < 128);
            Ok(ParsedSetting::Raw(BitSetting {
                start: bit,
                end: bit + 1,
                value,
            }))
        }
    } else {
        Ok(ParsedSetting::Named {
            key: key.to_string(),
            value: value_str.to_string(),
        })
    }
}

/// Resolve named settings against the core's config menu and collect all into BitSettings.
pub fn resolve_settings(
    core: &MisterFpgaCore,
    raw_settings: &[String],
) -> Result<Vec<BitSetting>> {
    let mut result = Vec::new();
    let config_menu = &core.config().menu;

    for s in raw_settings {
        match parse_setting_flexible(s)? {
            ParsedSetting::Raw(bit_setting) => {
                result.push(bit_setting);
            }
            ParsedSetting::Named { key, value } => {
                if let Some(setting) = resolve_named(config_menu, &key, &value) {
                    result.push(setting);
                } else {
                    warn!("Named setting '{key}={value}' not found in core config");
                }
            }
        }
    }

    Ok(result)
}

/// Search the core's config menu for a named option and resolve to a BitSetting.
fn resolve_named(menu: &[ConfigMenu], key: &str, value: &str) -> Option<BitSetting> {
    for item in menu {
        match item {
            ConfigMenu::Option {
                bits,
                label,
                choices,
            } => {
                if label.eq_ignore_ascii_case(key) {
                    // Try to match value as a choice name (case-insensitive)
                    if let Some(idx) = choices
                        .iter()
                        .position(|c| c.eq_ignore_ascii_case(value))
                    {
                        info!("Resolved setting '{key}' = '{value}' (choice {idx})");
                        return Some(BitSetting {
                            start: bits.start,
                            end: bits.end,
                            value: idx as u32,
                        });
                    }
                    // Try to parse value as a numeric choice index
                    if let Ok(idx) = value.parse::<u32>() {
                        info!("Resolved setting '{key}' = {idx} (numeric)");
                        return Some(BitSetting {
                            start: bits.start,
                            end: bits.end,
                            value: idx,
                        });
                    }
                    warn!("Setting '{key}': value '{value}' not found in choices: {choices:?}");
                    return None;
                }
            }
            // Recurse into pages
            ConfigMenu::PageItem(_, inner) => {
                if let Some(s) = resolve_named(std::slice::from_ref(inner.as_ref()), key, value) {
                    return Some(s);
                }
            }
            ConfigMenu::DisableIf(_, inner)
            | ConfigMenu::DisableUnless(_, inner)
            | ConfigMenu::HideIf(_, inner)
            | ConfigMenu::HideUnless(_, inner) => {
                if let Some(s) = resolve_named(std::slice::from_ref(inner.as_ref()), key, value) {
                    return Some(s);
                }
            }
            _ => {}
        }
    }
    None
}

/// Apply a list of raw bit settings to the core's status bits.
pub fn apply_settings(core: &mut MisterFpgaCore, settings: &[BitSetting]) -> Result<()> {
    if settings.is_empty() {
        return Ok(());
    }

    let mut bits: StatusBitMap = *core.status_bits();

    for setting in settings {
        info!(
            "Setting status bits {}..{} = {}",
            setting.start, setting.end, setting.value
        );
        bits.set_range(setting.start..setting.end, setting.value);
    }

    core.send_status_bits(bits);
    Ok(())
}
