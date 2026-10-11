use anyhow::{Context, Result};
use mister_fpga::core::MisterFpgaCore;
use one_fpga::core::SaveState as SaveStateTrait;
use std::fs;
use std::path::{Path, PathBuf};
use tracing::{debug, info, warn};

/// Build the save file path for a given system/rom/slot combination.
pub fn save_path(save_dir: &Path, system: &str, rom: &Path, slot: usize) -> PathBuf {
    let rom_stem = rom
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("unknown");
    save_dir
        .join("mister")
        .join(system)
        .join(format!("{rom_stem}_slot{slot}.sav"))
}

/// Save slot N to disk. Returns Ok(true) if saved, Ok(false) if not dirty or unsupported.
pub fn save_slot(core: &mut MisterFpgaCore, slot: usize, path: &Path) -> Result<bool> {
    let manager = match core.save_states_mut() {
        Some(m) => m,
        None => {
            debug!("Core does not support save states");
            return Ok(false);
        }
    };

    let slots = manager.slots_mut();
    if slot >= slots.len() {
        debug!("Save slot {slot} out of range (max {})", slots.len());
        return Ok(false);
    }

    if !slots[slot].is_dirty() {
        debug!("Save slot {slot} not dirty, skipping");
        return Ok(false);
    }

    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("Failed to create save directory: {}", parent.display()))?;
    }

    let mut file = fs::File::create(path)
        .with_context(|| format!("Failed to create save file: {}", path.display()))?;
    slots[slot]
        .save(&mut file)
        .map_err(|e| anyhow::anyhow!("Save state write failed: {e}"))?;

    info!("Saved state slot {slot} to {}", path.display());
    Ok(true)
}

/// Load slot N from disk. Returns Ok(true) if loaded, Ok(false) if file missing or unsupported.
pub fn load_slot(core: &mut MisterFpgaCore, slot: usize, path: &Path) -> Result<bool> {
    if !path.exists() {
        debug!("No save file at {}", path.display());
        return Ok(false);
    }

    let manager = match core.save_states_mut() {
        Some(m) => m,
        None => {
            debug!("Core does not support save states");
            return Ok(false);
        }
    };

    let slots = manager.slots_mut();
    if slot >= slots.len() {
        debug!("Save slot {slot} out of range (max {})", slots.len());
        return Ok(false);
    }

    let mut file = fs::File::open(path)
        .with_context(|| format!("Failed to open save file: {}", path.display()))?;
    slots[slot]
        .load(&mut file)
        .map_err(|e| anyhow::anyhow!("Save state load failed: {e}"))?;

    info!("Loaded state slot {slot} from {}", path.display());
    Ok(true)
}

/// Auto-save slot 0 if dirty.
pub fn autosave(
    core: &mut MisterFpgaCore,
    save_dir: &Path,
    rom: &Path,
    system: &str,
) -> Result<()> {
    let path = save_path(save_dir, system, rom, 0);
    match save_slot(core, 0, &path) {
        Ok(true) => info!("Autosave complete"),
        Ok(false) => debug!("Autosave skipped (not dirty or unsupported)"),
        Err(e) => warn!("Autosave failed: {e:#}"),
    }
    Ok(())
}

/// Auto-load slot 0 if a save file exists.
pub fn autoload(
    core: &mut MisterFpgaCore,
    save_dir: &Path,
    rom: &Path,
    system: &str,
) -> Result<()> {
    let path = save_path(save_dir, system, rom, 0);
    match load_slot(core, 0, &path) {
        Ok(true) => info!("Autoload complete"),
        Ok(false) => debug!("Autoload skipped (no save file or unsupported)"),
        Err(e) => warn!("Autoload failed: {e:#}"),
    }
    Ok(())
}
