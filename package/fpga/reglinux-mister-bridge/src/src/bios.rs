use anyhow::Result;
use mister_fpga::config_string::{ConfigMenu, FileExtension, LoadFileInfo};
use mister_fpga::core::MisterFpgaCore;
use std::path::{Path, PathBuf};
use tracing::info;

/// BIOS file entry: index at which to send the file to the FPGA core.
pub struct BiosFile {
    pub index: u8,
    pub path: PathBuf,
}

/// Send BIOS files to the core before ROM transfer.
///
/// Each entry specifies a file index (matching the core's config string F-section)
/// and a path to the BIOS file. Files are sent using the same FIO_FILE_TX protocol
/// as ROMs but at the core-specific BIOS slot index.
pub fn send_bios_files(core: &mut MisterFpgaCore, bios_files: &[BiosFile]) -> Result<()> {
    for bios in bios_files {
        let path = &bios.path;
        anyhow::ensure!(path.exists(), "BIOS file not found: {}", path.display());

        let ext_str = path
            .extension()
            .and_then(|e| e.to_str())
            .unwrap_or("bin")
            .to_uppercase();

        // Build a 3-byte padded extension
        let mut ext_bytes = [b' '; 3];
        for (i, b) in ext_str.bytes().take(3).enumerate() {
            ext_bytes[i] = b;
        }

        let file_info = LoadFileInfo {
            save_support: false,
            index: bios.index,
            extensions: vec![FileExtension(ext_bytes)],
            label: None,
            address: None,
        };

        let size = std::fs::metadata(path)
            .map(|m| m.len())
            .unwrap_or(0);

        info!(
            "Sending BIOS file {} (index={}, {} bytes)",
            path.display(),
            bios.index,
            size
        );

        core.load_file(path, Some(file_info))
            .map_err(|e| anyhow::anyhow!("BIOS transfer failed for {}: {e}", path.display()))?;
    }

    Ok(())
}

/// Auto-discover BIOS files for a system by scanning the core's config menu
/// and looking for matching files in the BIOS directory.
///
/// MiSTer convention: `boot.rom` / `boot0.rom` maps to the first F-section entry,
/// `boot1.rom` to the second, etc. We look for both REG-Linux standard BIOS names
/// and MiSTer boot.rom naming in the bios_dir.
pub fn auto_discover_bios(
    core: &MisterFpgaCore,
    system: &str,
    bios_dir: &Path,
) -> Vec<BiosFile> {
    let mut result = Vec::new();

    // Collect all LoadFile entries from the config (these are the BIOS/file slots)
    let load_entries: Vec<&LoadFileInfo> = collect_load_entries(&core.config().menu);

    if load_entries.is_empty() {
        return result;
    }

    // Try MiSTer-style boot ROM names first
    for (boot_idx, entry) in load_entries.iter().enumerate() {
        let boot_names = if boot_idx == 0 {
            vec!["boot.rom".to_string(), "boot0.rom".to_string()]
        } else {
            vec![format!("boot{boot_idx}.rom")]
        };

        for name in &boot_names {
            let path = bios_dir.join(name);
            if path.exists() {
                info!(
                    "Auto-discovered BIOS: {} → index {}",
                    path.display(),
                    entry.index
                );
                result.push(BiosFile {
                    index: entry.index,
                    path,
                });
                break;
            }
        }
    }

    // If we didn't find MiSTer-style boot ROMs, try REG-Linux BIOS names
    if result.is_empty() {
        if let Some(files) = reglinux_bios_files(system) {
            for (reg_idx, (filename, load_index)) in files.iter().enumerate() {
                let path = bios_dir.join(filename);
                if path.exists() {
                    // Use the explicit load_index if provided, otherwise use the
                    // config entry index for the Nth load slot
                    let index = load_index.unwrap_or_else(|| {
                        load_entries
                            .get(reg_idx)
                            .map(|e| e.index)
                            .unwrap_or(reg_idx as u8)
                    });
                    info!(
                        "Auto-discovered REG-Linux BIOS: {} → index {}",
                        path.display(),
                        index
                    );
                    result.push(BiosFile { index, path });
                }
            }
        }
    }

    result
}

/// Collect all LoadFile/LoadFileAndRemember entries from the config menu tree.
fn collect_load_entries(menu: &[ConfigMenu]) -> Vec<&LoadFileInfo> {
    let mut entries = Vec::new();
    for item in menu {
        match item {
            ConfigMenu::LoadFile(info) | ConfigMenu::LoadFileAndRemember(info) => {
                entries.push(info.as_ref());
            }
            ConfigMenu::PageItem(_, inner) => {
                entries.extend(collect_load_entries(std::slice::from_ref(inner.as_ref())));
            }
            ConfigMenu::DisableIf(_, inner)
            | ConfigMenu::DisableUnless(_, inner)
            | ConfigMenu::HideIf(_, inner)
            | ConfigMenu::HideUnless(_, inner) => {
                entries.extend(collect_load_entries(std::slice::from_ref(inner.as_ref())));
            }
            _ => {}
        }
    }
    entries
}

/// REG-Linux standard BIOS filenames for each system.
/// Returns a list of (filename, optional_explicit_index) pairs.
/// The index overrides the automatic F-section ordering when specified.
fn reglinux_bios_files(system: &str) -> Option<&'static [(&'static str, Option<u8>)]> {
    match system {
        // PlayStation: 3 regional BIOS files
        "psx" => Some(&[
            ("scph5501.bin", Some(0)),  // US BIOS
            ("scph5500.bin", Some(1)),  // JP BIOS
            ("scph5502.bin", Some(2)),  // EU BIOS
        ]),
        // GBA: optional but recommended
        "gba" => Some(&[("gba_bios.bin", Some(0))]),
        // NES FDS: disk system BIOS
        "fds" => Some(&[("disksys.rom", Some(0))]),
        // Saturn: regional BIOS
        "saturn" => Some(&[("saturn_bios.bin", Some(0))]),
        // ColecoVision
        "colecovision" => Some(&[("colecovision.rom", Some(0))]),
        // Intellivision
        "intellivision" => Some(&[
            ("exec.bin", Some(0)),
            ("grom.bin", Some(1)),
        ]),
        // Atari 5200 / 800
        "atari5200" | "atari800" => Some(&[("ATARIXL.ROM", Some(0))]),
        // Lynx
        "lynx" => Some(&[("lynxboot.img", Some(0))]),
        // TI-99/4A
        "ti99" => Some(&[
            ("994aROM.Bin", Some(0)),
            ("994aGROM.Bin", Some(1)),
        ]),
        // CoCo3
        "coco" => Some(&[
            ("coco3.rom", Some(0)),
            ("disk11.rom", Some(1)),
        ]),
        _ => None,
    }
}
