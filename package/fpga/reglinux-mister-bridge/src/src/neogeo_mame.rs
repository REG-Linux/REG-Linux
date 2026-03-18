use anyhow::{Context, Result};
use mister_fpga::core::MisterFpgaCore;
use std::fs;
use std::io::Cursor;
use std::path::Path;
use tracing::{debug, info, warn};

use crate::neogeo;

/// Per-game hardware quirk flags parsed from romsets.xml.
#[derive(Debug, Default)]
#[allow(dead_code)]
struct GameQuirks {
    rom_wait: bool,
    p_wait: bool,
    /// PCM mode: 0=separate V1/V2, 1=merged V1 only, 2=large V1 (>16MB)
    pcm: u8,
}

/// A single ROM file entry from romsets.xml.
#[derive(Debug)]
struct RomFile {
    name: String,
    rom_type: char, // P, S, M, V, C
    index: u8,
    offset: u64,
    length: Option<u64>,
}

/// A parsed romset entry.
#[derive(Debug)]
struct Romset {
    name: String,
    files: Vec<RomFile>,
    quirks: GameQuirks,
}

/// Load a NeoGeo MAME-format ROM set from a directory.
///
/// Looks for romsets.xml in the ROM directory or its parent to find the game
/// entry, then loads individual ROM files, concatenates/interleaves as needed,
/// and sends each section to the FPGA core.
pub fn load_mame_romset(core: &mut MisterFpgaCore, rom_dir: &Path) -> Result<()> {
    let dir_name = rom_dir
        .file_name()
        .and_then(|n| n.to_str())
        .context("Invalid ROM directory name")?;

    // Find romsets.xml: check inside the directory, then parent
    let xml_path = find_romsets_xml(rom_dir)?;
    info!(
        "NeoGeo MAME: loading '{}' using {}",
        dir_name,
        xml_path.display()
    );

    let xml_content = fs::read_to_string(&xml_path)
        .with_context(|| format!("Failed to read {}", xml_path.display()))?;

    let romset = parse_romset(&xml_content, dir_name)
        .with_context(|| format!("Game '{}' not found in romsets.xml", dir_name))?;

    info!(
        "NeoGeo MAME: found '{}' with {} ROM files (rom_wait={}, p_wait={})",
        romset.name,
        romset.files.len(),
        romset.quirks.rom_wait,
        romset.quirks.p_wait,
    );

    // Group files by type and load each section
    let p_files: Vec<&RomFile> = romset.files.iter().filter(|f| f.rom_type == 'P').collect();
    let s_files: Vec<&RomFile> = romset.files.iter().filter(|f| f.rom_type == 'S').collect();
    let m_files: Vec<&RomFile> = romset.files.iter().filter(|f| f.rom_type == 'M').collect();
    let v_files: Vec<&RomFile> = romset.files.iter().filter(|f| f.rom_type == 'V').collect();
    let c_files: Vec<&RomFile> = romset.files.iter().filter(|f| f.rom_type == 'C').collect();

    // P-ROM (program) → index 4
    if !p_files.is_empty() {
        let p_data = concat_rom_files(rom_dir, &p_files)?;
        let p_size = p_data.len() as u32;
        let mut cursor = Cursor::new(p_data);
        neogeo::send_section_raw(core, &mut cursor, 0, p_size, 4)?;
        let notify_size = (p_size + neogeo::ALIGN_1MB) & !neogeo::ALIGN_1MB;
        neogeo::notify_core(core, 4, notify_size)?;
    }

    // S-ROM (fix/tiles) → index 8
    if !s_files.is_empty() {
        let s_data = concat_rom_files(rom_dir, &s_files)?;
        let s_size = s_data.len() as u32;
        let mut cursor = Cursor::new(s_data);
        neogeo::send_section_fix(core, &mut cursor, 0, s_size, 8)?;
        neogeo::notify_core(core, 8, s_size)?;
    }

    // M-ROM (Z80 sound) → index 9
    if !m_files.is_empty() {
        let m_data = concat_rom_files(rom_dir, &m_files)?;
        let m_size = m_data.len() as u32;
        let mut cursor = Cursor::new(m_data);
        neogeo::send_section_raw(core, &mut cursor, 0, m_size, 9)?;
        neogeo::notify_core(core, 9, m_size)?;
    }

    // V-ROMs (voice/ADPCM)
    // Split into V1 (indices with index < 2) and V2 (index >= 2)
    let v1_files: Vec<&RomFile> = v_files.iter().filter(|f| f.index < 2).copied().collect();
    let v2_files: Vec<&RomFile> = v_files.iter().filter(|f| f.index >= 2).copied().collect();

    let mut use_pcm: u32 = 0;
    if !v1_files.is_empty() {
        let v1_data = concat_rom_files(rom_dir, &v1_files)?;
        let v1_size = v1_data.len() as u32;
        let mut cursor = Cursor::new(v1_data);
        neogeo::send_section_raw(core, &mut cursor, 0, v1_size, 16)?;
        neogeo::notify_core(core, 16, v1_size)?;

        if !v2_files.is_empty() {
            let v2_data = concat_rom_files(rom_dir, &v2_files)?;
            let v2_size = v2_data.len() as u32;
            let mut cursor = Cursor::new(v2_data);
            neogeo::send_section_raw(core, &mut cursor, 0, v2_size, 48)?;
            neogeo::notify_core(core, 48, v2_size)?;
        } else if v1_size > 16 * 1024 * 1024 {
            use_pcm = 2;
        } else {
            use_pcm = 1;
        }
    }

    // C-ROMs (sprites) → index 15
    // C-ROMs come in pairs (c1+c2, c3+c4, ...) that must be byte-interleaved
    if !c_files.is_empty() {
        let c_data = interleave_c_roms(rom_dir, &c_files)?;
        let c_size = c_data.len() as u32;
        let mut cursor = Cursor::new(c_data);
        neogeo::send_section_spr(core, &mut cursor, 0, c_size, 15)?;
        neogeo::notify_core(core, 15, c_size)?;
    }

    // Set PCM config bits
    neogeo::set_config_bit(core, 23, if use_pcm > 0 { 1 } else { 0 });
    neogeo::set_config_bit(core, 19, if use_pcm == 2 { 1 } else { 0 });

    info!("NeoGeo MAME ROM loading complete");
    Ok(())
}

/// Find romsets.xml searching in: game dir → parent dir → grandparent/NEOGEO dir.
fn find_romsets_xml(rom_dir: &Path) -> Result<std::path::PathBuf> {
    // Check for per-game romset.xml (singular) first
    let single = rom_dir.join("romset.xml");
    if single.exists() {
        return Ok(single);
    }

    // Check in the ROM directory itself
    let in_dir = rom_dir.join("romsets.xml");
    if in_dir.exists() {
        return Ok(in_dir);
    }

    // Check parent directory
    if let Some(parent) = rom_dir.parent() {
        let in_parent = parent.join("romsets.xml");
        if in_parent.exists() {
            return Ok(in_parent);
        }
    }

    anyhow::bail!(
        "romsets.xml not found for {}. Place it in the game directory or its parent.",
        rom_dir.display()
    )
}

/// Parse romsets.xml and find the entry matching the given game name.
fn parse_romset(xml: &str, game_name: &str) -> Result<Romset> {
    let doc = roxmltree::Document::parse(xml)
        .context("Failed to parse romsets.xml")?;

    let root = doc.root_element();

    for node in root.children() {
        if !node.is_element() {
            continue;
        }
        // Match <romset> or <game> elements
        if node.tag_name().name() != "romset" && node.tag_name().name() != "game" {
            continue;
        }

        let name = node.attribute("name").unwrap_or("");
        let altname = node.attribute("altname").unwrap_or("");

        if !name.eq_ignore_ascii_case(game_name) && !altname.eq_ignore_ascii_case(game_name) {
            continue;
        }

        // Parse quirk attributes
        let quirks = GameQuirks {
            rom_wait: node.attribute("rom_wait").and_then(|v| v.parse().ok()).unwrap_or(false),
            p_wait: node.attribute("p_wait").and_then(|v| v.parse().ok()).unwrap_or(false),
            pcm: node.attribute("pcm").and_then(|v| v.parse().ok()).unwrap_or(0),
        };

        // Parse ROM file entries
        let mut files = Vec::new();
        for child in node.children() {
            if !child.is_element() || child.tag_name().name() != "file" {
                continue;
            }

            let file_name = child.attribute("name").unwrap_or("").to_string();
            let rom_type = child
                .attribute("type")
                .and_then(|t| t.chars().next())
                .unwrap_or('P');
            let index: u8 = child
                .attribute("index")
                .and_then(|v| v.parse().ok())
                .unwrap_or(0);
            let offset: u64 = child
                .attribute("offset")
                .and_then(|v| parse_hex_or_dec(v))
                .unwrap_or(0);
            let length: Option<u64> = child
                .attribute("length")
                .and_then(|v| parse_hex_or_dec(v));

            if !file_name.is_empty() {
                files.push(RomFile {
                    name: file_name,
                    rom_type,
                    index,
                    offset,
                    length,
                });
            }
        }

        return Ok(Romset {
            name: name.to_string(),
            files,
            quirks,
        });
    }

    anyhow::bail!("Game '{}' not found in romsets.xml", game_name)
}

/// Parse a string as hex (0x prefix) or decimal.
fn parse_hex_or_dec(s: &str) -> Option<u64> {
    if let Some(hex) = s.strip_prefix("0x").or_else(|| s.strip_prefix("0X")) {
        u64::from_str_radix(hex, 16).ok()
    } else {
        s.parse().ok()
    }
}

/// Read and concatenate ROM files in index order.
fn concat_rom_files(rom_dir: &Path, files: &[&RomFile]) -> Result<Vec<u8>> {
    let mut sorted: Vec<&&RomFile> = files.iter().collect();
    sorted.sort_by_key(|f| f.index);

    let mut data = Vec::new();
    for file in sorted {
        let path = rom_dir.join(&file.name);
        if !path.exists() {
            warn!("ROM file not found: {}, skipping", path.display());
            continue;
        }

        let file_data = fs::read(&path)
            .with_context(|| format!("Failed to read ROM file: {}", path.display()))?;

        let start = file.offset as usize;
        let end = file
            .length
            .map(|l| (start + l as usize).min(file_data.len()))
            .unwrap_or(file_data.len());

        if start < file_data.len() {
            data.extend_from_slice(&file_data[start..end]);
            debug!(
                "Read {} bytes from {} (offset={}, len={})",
                end - start,
                file.name,
                start,
                end - start
            );
        }
    }

    Ok(data)
}

/// Interleave C-ROM pairs for sprite data.
///
/// C-ROMs come in pairs (odd/even indices): c1+c2, c3+c4, c5+c6, etc.
/// Each pair is byte-interleaved: take alternating bytes from each file.
fn interleave_c_roms(rom_dir: &Path, files: &[&RomFile]) -> Result<Vec<u8>> {
    let mut sorted: Vec<&&RomFile> = files.iter().collect();
    sorted.sort_by_key(|f| f.index);

    let mut result = Vec::new();

    // Process in pairs
    let mut i = 0;
    while i < sorted.len() {
        let file_a = sorted[i];
        let path_a = rom_dir.join(&file_a.name);
        let data_a = fs::read(&path_a)
            .with_context(|| format!("Failed to read C-ROM: {}", path_a.display()))?;

        if i + 1 < sorted.len() {
            let file_b = sorted[i + 1];
            let path_b = rom_dir.join(&file_b.name);
            let data_b = fs::read(&path_b)
                .with_context(|| format!("Failed to read C-ROM: {}", path_b.display()))?;

            let len = data_a.len().max(data_b.len());
            debug!(
                "Interleaving C-ROM pair: {} + {} ({} bytes each)",
                file_a.name, file_b.name, len
            );

            // Byte-interleave: [a0, b0, a1, b1, a2, b2, ...]
            for j in 0..len {
                result.push(*data_a.get(j).unwrap_or(&0));
                result.push(*data_b.get(j).unwrap_or(&0));
            }

            i += 2;
        } else {
            // Odd file out — append directly
            warn!("Unpaired C-ROM file: {}", file_a.name);
            result.extend_from_slice(&data_a);
            i += 1;
        }
    }

    Ok(result)
}
