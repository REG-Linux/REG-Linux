use anyhow::{Context, Result};
use std::fs::{self, File};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::{Path, PathBuf};
use tracing::{debug, info, warn};

/// Resolve a CD image path to a raw mountable file.
///
/// - `.cue` → parse to find the referenced BIN/ISO file, return its path
/// - `.chd` → decompress to a temp file, return the temp path
/// - anything else → return the path as-is (raw image)
///
/// Returns the resolved path. For CHD, the caller should clean up the temp file
/// when done (returned via `TempCdImage`).
pub fn resolve_cd_image(path: &Path) -> Result<CdImage> {
    let ext = path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();

    match ext.as_str() {
        "cue" => match parse_cue_bin(path)? {
            CueParsed::Single(bin_path) => {
                info!("CUE resolved to: {}", bin_path.display());
                Ok(CdImage::Direct(bin_path))
            }
            CueParsed::Concatenated(temp_path) => {
                info!("CUE multi-BIN concatenated to: {}", temp_path.display());
                Ok(CdImage::Temp(temp_path))
            }
        },
        "chd" => {
            let temp_path = decompress_chd(path)?;
            info!("CHD decompressed to: {}", temp_path.display());
            Ok(CdImage::Temp(temp_path))
        }
        _ => Ok(CdImage::Direct(path.to_path_buf())),
    }
}

/// Resolved CD image: either a direct path or a temporary decompressed file.
pub enum CdImage {
    /// Use this path directly (raw image or resolved BIN from CUE).
    Direct(PathBuf),
    /// Temporary decompressed file (CHD). Should be cleaned up when done.
    Temp(PathBuf),
}

impl CdImage {
    /// Get the path to the mountable file.
    pub fn path(&self) -> &Path {
        match self {
            CdImage::Direct(p) | CdImage::Temp(p) => p,
        }
    }

    /// Clean up any temporary files.
    pub fn cleanup(&self) {
        if let CdImage::Temp(p) = self {
            if p.exists() {
                if let Err(e) = fs::remove_file(p) {
                    warn!("Failed to remove temp CD image {}: {e}", p.display());
                } else {
                    debug!("Cleaned up temp CD image: {}", p.display());
                }
            }
        }
    }
}

impl Drop for CdImage {
    fn drop(&mut self) {
        self.cleanup();
    }
}

/// Parse a CUE file and resolve to a single mountable BIN path.
///
/// For single-FILE CUE sheets (most common), returns the BIN path directly.
/// For multi-FILE CUE sheets, concatenates all BIN files into a temp file.
fn parse_cue_bin(cue_path: &Path) -> Result<CueParsed> {
    let cue_dir = cue_path
        .parent()
        .unwrap_or_else(|| Path::new("."));

    let file = File::open(cue_path)
        .with_context(|| format!("Failed to open CUE file: {}", cue_path.display()))?;

    let reader = BufReader::new(file);
    let mut bin_paths: Vec<PathBuf> = Vec::new();

    for line in reader.lines() {
        let line = line?;
        let trimmed = line.trim();

        // Look for FILE directive: FILE "name" BINARY or FILE name BINARY
        if !trimmed.to_uppercase().starts_with("FILE ") {
            continue;
        }

        let rest = trimmed[5..].trim();
        let filename = if rest.starts_with('"') {
            // Quoted filename: FILE "some file.bin" BINARY
            rest[1..]
                .find('"')
                .map(|end| &rest[1..end + 1])
                .unwrap_or(rest)
        } else {
            // Unquoted: FILE game.bin BINARY
            rest.split_whitespace().next().unwrap_or(rest)
        };

        if filename.is_empty() {
            continue;
        }

        let bin_path = cue_dir.join(filename);
        if bin_path.exists() {
            bin_paths.push(bin_path);
        } else if let Some(found) = find_file_case_insensitive(cue_dir, filename) {
            bin_paths.push(found);
        } else {
            anyhow::bail!(
                "BIN file referenced in CUE not found: {} (from {})",
                filename,
                cue_path.display()
            );
        }
    }

    if bin_paths.is_empty() {
        anyhow::bail!(
            "No FILE directive found in CUE file: {}",
            cue_path.display()
        );
    }

    if bin_paths.len() == 1 {
        // Single-BIN CUE: use the BIN directly
        return Ok(CueParsed::Single(bin_paths.remove(0)));
    }

    // Multi-BIN CUE: concatenate all BIN files into a temp file
    let temp_path = cue_path.with_extension("tmp.bin");
    info!(
        "Multi-BIN CUE: concatenating {} files into {}",
        bin_paths.len(),
        temp_path.display()
    );

    let out_file = File::create(&temp_path)
        .with_context(|| format!("Failed to create temp file: {}", temp_path.display()))?;
    let mut writer = BufWriter::new(out_file);
    let mut total: u64 = 0;

    for bin in &bin_paths {
        let data = fs::read(bin)
            .with_context(|| format!("Failed to read BIN file: {}", bin.display()))?;
        writer.write_all(&data)?;
        total += data.len() as u64;
        debug!("Concatenated {} ({} bytes)", bin.display(), data.len());
    }

    writer.flush()?;
    info!("Multi-BIN CUE: {} bytes total", total);

    Ok(CueParsed::Concatenated(temp_path))
}

/// Result of CUE parsing.
enum CueParsed {
    /// Single BIN file, use directly.
    Single(PathBuf),
    /// Multiple BIN files concatenated into a temp file.
    Concatenated(PathBuf),
}

/// Case-insensitive file search in a directory.
fn find_file_case_insensitive(dir: &Path, filename: &str) -> Option<PathBuf> {
    let lower = filename.to_lowercase();
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            if let Some(name) = entry.file_name().to_str() {
                if name.to_lowercase() == lower {
                    return Some(entry.path());
                }
            }
        }
    }
    None
}

/// Decompress a CHD file to a temporary raw image file.
///
/// Uses the `chd` crate to read hunks and write raw sector data.
/// The temp file is placed alongside the CHD with a `.tmp.bin` extension.
fn decompress_chd(chd_path: &Path) -> Result<PathBuf> {
    let temp_path = chd_path.with_extension("tmp.bin");

    // Skip decompression if temp file already exists and is newer than CHD
    if temp_path.exists() {
        let chd_modified = fs::metadata(chd_path)
            .and_then(|m| m.modified())
            .ok();
        let tmp_modified = fs::metadata(&temp_path)
            .and_then(|m| m.modified())
            .ok();

        if let (Some(chd_time), Some(tmp_time)) = (chd_modified, tmp_modified) {
            if tmp_time > chd_time {
                info!("Using cached CHD decompression: {}", temp_path.display());
                return Ok(temp_path);
            }
        }
    }

    info!(
        "Decompressing CHD: {} (this may take a moment...)",
        chd_path.display()
    );

    let mut chd_file = BufReader::new(
        File::open(chd_path)
            .with_context(|| format!("Failed to open CHD: {}", chd_path.display()))?,
    );

    let mut chd = chd::Chd::open(&mut chd_file, None)
        .map_err(|e| anyhow::anyhow!("Failed to parse CHD: {e}"))?;

    let header = chd.header();
    let hunk_size = header.hunk_size() as usize;
    let num_hunks = header.hunk_count();
    let logical_bytes = header.logical_bytes();

    info!(
        "CHD: {} hunks x {} bytes = {} MB logical",
        num_hunks,
        hunk_size,
        logical_bytes / (1024 * 1024),
    );

    let out_file = File::create(&temp_path)
        .with_context(|| format!("Failed to create temp file: {}", temp_path.display()))?;
    let mut writer = BufWriter::new(out_file);

    let mut hunk_buf = vec![0u8; hunk_size];
    let mut compressed_buf: Vec<u8> = Vec::new();
    let mut written: u64 = 0;

    for hunk_idx in 0..num_hunks {
        let mut hunk = chd
            .hunk(hunk_idx)
            .map_err(|e| anyhow::anyhow!("Failed to read CHD hunk {hunk_idx}: {e}"))?;
        hunk.read_hunk_in(&mut compressed_buf, &mut hunk_buf)
            .map_err(|e| anyhow::anyhow!("Failed to decompress CHD hunk {hunk_idx}: {e}"))?;

        // Don't write beyond logical size
        let remaining = (logical_bytes - written) as usize;
        let to_write = remaining.min(hunk_size);
        writer.write_all(&hunk_buf[..to_write])?;
        written += to_write as u64;

        if hunk_idx % 1000 == 0 && hunk_idx > 0 {
            debug!(
                "CHD decompression: {:.0}%",
                (hunk_idx as f64 / num_hunks as f64) * 100.0
            );
        }
    }

    writer.flush()?;
    info!(
        "CHD decompressed: {} bytes written to {}",
        written,
        temp_path.display()
    );

    Ok(temp_path)
}
