use anyhow::{Context, Result};
use mister_fpga::core::MisterFpgaCore;
use mister_fpga::fpga::file_io::{
    FileExtension, FileIndex, FileTxData16Bits, FileTxData8Bits, FileTxDisabled, FileTxEnabled,
};
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;
use tracing::{info, warn};

/// .neo file header (4096 bytes total, first 512 are meaningful).
#[derive(Debug)]
struct NeoHeader {
    p_size: u32,
    s_size: u32,
    m_size: u32,
    v1_size: u32,
    v2_size: u32,
    c_size: u32,
    ngh: u32,
    name: String,
}

const NEO_HEADER_SIZE: u64 = 4096;

/// Chunk size for streaming ROM data through SPI (64KB = 1024 * 64-byte blocks).
pub(crate) const CHUNK_SIZE: usize = 64 * 1024;

/// 1MB alignment mask for P-ROM notify.
pub(crate) const ALIGN_1MB: u32 = 0xF_FFFF;

/// Load a NeoGeo .neo file into the FPGA core.
///
/// .neo files have a 4096-byte header followed by concatenated ROM sections:
/// P (program), S (fix tiles), M (Z80 audio), V1 (voice), V2 (voice), C (sprites).
/// Each section is sent at a specific FPGA index with appropriate data conversion.
pub fn load_neo(core: &mut MisterFpgaCore, neo_path: &Path) -> Result<()> {
    let mut file = File::open(neo_path)
        .with_context(|| format!("Failed to open .neo file: {}", neo_path.display()))?;

    let header = parse_header(&mut file)?;
    info!(
        "NeoGeo: NGH=0x{:X} P={}K S={}K M={}K V1={}K V2={}K C={}K \"{}\"",
        header.ngh,
        header.p_size / 1024,
        header.s_size / 1024,
        header.m_size / 1024,
        header.v1_size / 1024,
        header.v2_size / 1024,
        header.c_size / 1024,
        header.name,
    );

    let mut offset = NEO_HEADER_SIZE;

    // P-ROM (program) → index 4, raw
    if header.p_size > 0 {
        send_section_raw(core, &mut file, offset, header.p_size, 4)?;
        let notify_size = (header.p_size + ALIGN_1MB) & !ALIGN_1MB;
        notify_core(core, 4, notify_size)?;
        offset += header.p_size as u64;
    }

    // S-ROM (fix/tiles) → index 8, fix_convert
    if header.s_size > 0 {
        send_section_fix(core, &mut file, offset, header.s_size, 8)?;
        notify_core(core, 8, header.s_size)?;
        offset += header.s_size as u64;
    }

    // M-ROM (Z80 sound) → index 9, raw
    if header.m_size > 0 {
        send_section_raw(core, &mut file, offset, header.m_size, 9)?;
        notify_core(core, 9, header.m_size)?;
        offset += header.m_size as u64;
    }

    // V1-ROM (voice) → index 16, raw
    if header.v1_size > 0 {
        send_section_raw(core, &mut file, offset, header.v1_size, 16)?;
        notify_core(core, 16, header.v1_size)?;
        offset += header.v1_size as u64;
    }

    // V2-ROM (voice bank 2) → index 48, raw
    let use_pcm;
    if header.v2_size > 0 {
        use_pcm = 0u32;
        send_section_raw(core, &mut file, offset, header.v2_size, 48)?;
        notify_core(core, 48, header.v2_size)?;
        offset += header.v2_size as u64;
    } else if header.v1_size > 16 * 1024 * 1024 {
        use_pcm = 2;
    } else {
        use_pcm = 1;
    }

    // C-ROM (sprites) → index 15, spr_convert
    if header.c_size > 0 {
        send_section_spr(core, &mut file, offset, header.c_size, 15)?;
        notify_core(core, 15, header.c_size)?;
    }

    // Set PCM config bit (bit 23)
    set_config_bit(core, 23, if use_pcm > 0 { 1 } else { 0 });
    // Set PCM2 config bit (bit 19) for V1 > 16MB without V2
    set_config_bit(core, 19, if use_pcm == 2 { 1 } else { 0 });

    info!("NeoGeo ROM loading complete");
    Ok(())
}

/// Parse the .neo file header.
fn parse_header(file: &mut File) -> Result<NeoHeader> {
    let mut buf = [0u8; 512];
    file.read_exact(&mut buf)
        .context("Failed to read .neo header")?;

    // Verify magic: bytes 0-2 should be "NEO" (0x4E, 0x45, 0x4F)
    if buf[0] != 0x4E || buf[1] != 0x45 || buf[2] != 0x4F {
        warn!(
            "NeoGeo: non-standard header magic: {:02X} {:02X} {:02X}",
            buf[0], buf[1], buf[2]
        );
    }

    let p_size = u32::from_le_bytes([buf[4], buf[5], buf[6], buf[7]]);
    let s_size = u32::from_le_bytes([buf[8], buf[9], buf[10], buf[11]]);
    let m_size = u32::from_le_bytes([buf[12], buf[13], buf[14], buf[15]]);
    let v1_size = u32::from_le_bytes([buf[16], buf[17], buf[18], buf[19]]);
    let v2_size = u32::from_le_bytes([buf[20], buf[21], buf[22], buf[23]]);
    let c_size = u32::from_le_bytes([buf[24], buf[25], buf[26], buf[27]]);
    let ngh = u32::from_le_bytes([buf[40], buf[41], buf[42], buf[43]]);

    // Name is at offset 44, up to 33 bytes, null-terminated
    let name_bytes = &buf[44..77];
    let name = String::from_utf8_lossy(
        &name_bytes[..name_bytes.iter().position(|&b| b == 0).unwrap_or(33)],
    )
    .to_string();

    Ok(NeoHeader {
        p_size,
        s_size,
        m_size,
        v1_size,
        v2_size,
        c_size,
        ngh,
        name,
    })
}

/// Send a raw ROM section (no conversion) via SPI file transfer.
pub(crate) fn send_section_raw(
    core: &mut MisterFpgaCore,
    file: &mut (impl Read + Seek),
    offset: u64,
    size: u32,
    index: u8,
) -> Result<()> {
    info!("NeoGeo: sending section index={index} offset={offset} size={size}");
    file.seek(SeekFrom::Start(offset))?;

    let spi = core.spi_mut();
    spi.execute(FileIndex::new(index))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileExtension("ROM"))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileTxEnabled(Some(size)))
        .map_err(|e| anyhow::anyhow!("{e}"))?;

    let mut remaining = size as usize;
    let mut buf = vec![0u8; CHUNK_SIZE];
    while remaining > 0 {
        let to_read = remaining.min(CHUNK_SIZE);
        file.read_exact(&mut buf[..to_read])?;
        spi.execute(FileTxData8Bits(&buf[..to_read]))
            .map_err(|e| anyhow::anyhow!("{e}"))?;
        remaining -= to_read;
    }

    spi.execute(FileTxDisabled)
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    Ok(())
}

/// Send a fix/tile ROM section with fix_convert applied.
///
/// fix_convert reorders bytes within 32-byte blocks:
/// output[i] = input[(i & ~0x1F) | ((i >> 2) & 7) | ((i & 1) << 3) | (((i & 2) << 3) ^ 0x10)]
pub(crate) fn send_section_fix(
    core: &mut MisterFpgaCore,
    file: &mut (impl Read + Seek),
    offset: u64,
    size: u32,
    index: u8,
) -> Result<()> {
    info!("NeoGeo: sending FIX section index={index} offset={offset} size={size}");
    file.seek(SeekFrom::Start(offset))?;

    let spi = core.spi_mut();
    spi.execute(FileIndex::new(index))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileExtension("ROM"))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileTxEnabled(Some(size)))
        .map_err(|e| anyhow::anyhow!("{e}"))?;

    let mut remaining = size as usize;
    let mut buf_in = vec![0u8; CHUNK_SIZE];
    let mut buf_out = vec![0u8; CHUNK_SIZE];
    while remaining > 0 {
        let to_read = remaining.min(CHUNK_SIZE);
        file.read_exact(&mut buf_in[..to_read])?;
        fix_convert(&buf_in[..to_read], &mut buf_out[..to_read]);
        spi.execute(FileTxData8Bits(&buf_out[..to_read]))
            .map_err(|e| anyhow::anyhow!("{e}"))?;
        remaining -= to_read;
    }

    spi.execute(FileTxDisabled)
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    Ok(())
}

/// Send a sprite ROM section with spr_convert applied.
///
/// spr_convert reorders 16-bit words within 32-word (64-byte) blocks:
/// output[i] = input[(i & ~0x1F) | ((i >> 1) & 0xF) | (((i & 1) ^ 1) << 4)]
pub(crate) fn send_section_spr(
    core: &mut MisterFpgaCore,
    file: &mut (impl Read + Seek),
    offset: u64,
    size: u32,
    index: u8,
) -> Result<()> {
    info!("NeoGeo: sending SPR section index={index} offset={offset} size={size}");
    file.seek(SeekFrom::Start(offset))?;

    let spi = core.spi_mut();
    spi.execute(FileIndex::new(index))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileExtension("ROM"))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileTxEnabled(Some(size)))
        .map_err(|e| anyhow::anyhow!("{e}"))?;

    let word_count = size as usize / 2;
    let mut remaining_words = word_count;
    let chunk_words = CHUNK_SIZE / 2;
    let mut buf_in = vec![0u16; chunk_words];
    let mut buf_out = vec![0u16; chunk_words];
    let mut byte_buf = vec![0u8; CHUNK_SIZE];

    while remaining_words > 0 {
        let to_read = remaining_words.min(chunk_words);
        let to_read_bytes = to_read * 2;
        file.read_exact(&mut byte_buf[..to_read_bytes])?;

        // Convert bytes to u16 (little-endian)
        for i in 0..to_read {
            buf_in[i] = u16::from_le_bytes([byte_buf[i * 2], byte_buf[i * 2 + 1]]);
        }

        spr_convert(&buf_in[..to_read], &mut buf_out[..to_read]);

        spi.execute(FileTxData16Bits(&buf_out[..to_read]))
            .map_err(|e| anyhow::anyhow!("{e}"))?;
        remaining_words -= to_read;
    }

    // Handle odd trailing byte if size is not word-aligned
    if size % 2 != 0 {
        let mut trail = [0u8; 1];
        file.read_exact(&mut trail)?;
        spi.execute(FileTxData8Bits(&trail))
            .map_err(|e| anyhow::anyhow!("{e}"))?;
    }

    spi.execute(FileTxDisabled)
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    Ok(())
}

/// NeoGeo fix/tile data conversion.
/// Reorders bytes within 32-byte blocks for efficient FPGA access.
fn fix_convert(input: &[u8], output: &mut [u8]) {
    for i in 0..input.len() {
        let src = (i & !0x1F) | ((i >> 2) & 7) | ((i & 1) << 3) | (((i & 2) << 3) ^ 0x10);
        if src < input.len() {
            output[i] = input[src];
        }
    }
}

/// NeoGeo sprite data conversion.
/// Reorders 16-bit words within 32-word (64-byte) blocks for efficient SDRAM burst reads.
fn spr_convert(input: &[u16], output: &mut [u16]) {
    for i in 0..input.len() {
        let src = (i & !0x1F) | ((i >> 1) & 0xF) | (((i & 1) ^ 1) << 4);
        if src < input.len() {
            output[i] = input[src];
        }
    }
}

/// Send the NeoGeo notify protocol to inform the core about a loaded ROM section.
///
/// Uses FPGA index 10 as a metadata notification channel:
/// sends [rom_type, size_low, size_high, memcp, 0] as 16-bit words.
pub(crate) fn notify_core(core: &mut MisterFpgaCore, rom_index: u8, size: u32) -> Result<()> {
    // memcp = 1 for most ROM types, 0 for M-ROM (index 9) and V-ROM (index 16-63)
    let memcp: u16 = if rom_index == 9 || (rom_index >= 16 && rom_index < 64) {
        0
    } else {
        1
    };

    let data: [u16; 5] = [
        rom_index as u16,
        size as u16,
        (size >> 16) as u16,
        memcp,
        0,
    ];

    let spi = core.spi_mut();
    spi.execute(FileIndex::new(10))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileTxEnabled(None))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileTxData16Bits(&data))
        .map_err(|e| anyhow::anyhow!("{e}"))?;
    spi.execute(FileTxDisabled)
        .map_err(|e| anyhow::anyhow!("{e}"))?;

    Ok(())
}

/// Set a single config/status bit on the core.
pub(crate) fn set_config_bit(core: &mut MisterFpgaCore, bit: u8, value: u32) {
    let mut bits = *core.status_bits();
    bits.set_range(bit..bit + 1, value);
    core.send_status_bits(bits);
}
