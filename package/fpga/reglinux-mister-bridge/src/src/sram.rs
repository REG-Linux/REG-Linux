use anyhow::{Context, Result};
use mister_fpga::core::file::SdCard;
use mister_fpga::core::MisterFpgaCore;
use std::fs::{self, File};
use std::path::{Path, PathBuf};
use tracing::{debug, info};

/// Detect whether the loaded core supports battery-backed SRAM for the given ROM.
///
/// Checks the core's config string for a file entry matching the ROM extension
/// with `save_support` enabled (FS prefix in config string).
/// Returns the file slot index if save support is found.
pub fn detect_save_support(core: &MisterFpgaCore, rom_path: &Path) -> Option<u8> {
    let config = core.config();
    let load_info = config.load_info(rom_path).ok()??;
    if load_info.save_support {
        Some(load_info.index)
    } else {
        None
    }
}

/// Build the SRAM save file path for a given system and ROM.
///
/// Convention: `/userdata/saves/mister/{system}/{rom_stem}.srm`
pub fn sram_path(saves_dir: &Path, system: &str, rom: &Path) -> PathBuf {
    let rom_stem = rom
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("unknown");
    saves_dir.join(system).join(format!("{rom_stem}.srm"))
}

/// Mount an SRAM save file for battery-backed save support.
///
/// Creates the save file if it doesn't exist (the core will initialize SRAM).
/// The file is mounted as a writable SD card at the given slot index.
/// `poll_mounts()` in the input loop handles ongoing read/write I/O.
pub fn mount_sram(core: &mut MisterFpgaCore, sav_path: &Path, index: u8) -> Result<()> {
    if let Some(parent) = sav_path.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("Failed to create SRAM directory: {}", parent.display()))?;
    }

    // Create empty save file if it doesn't exist
    if !sav_path.exists() {
        File::create(sav_path)
            .with_context(|| format!("Failed to create SRAM file: {}", sav_path.display()))?;
        debug!("Created new SRAM file: {}", sav_path.display());
    }

    let card = SdCard::from_path(sav_path)
        .map_err(|e| anyhow::anyhow!("Failed to open SRAM file {}: {e}", sav_path.display()))?;

    core.mount(card, index)
        .map_err(|e| anyhow::anyhow!("Failed to mount SRAM at slot {index}: {e}"))?;

    info!("SRAM mounted: {} at slot {}", sav_path.display(), index);
    Ok(())
}
