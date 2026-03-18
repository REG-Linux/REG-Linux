use anyhow::Result;
use mister_fpga::core::MisterFpgaCore;
use std::path::Path;
use tracing::info;

/// Send a ROM file to the loaded FPGA core using the FIO_FILE_TX protocol.
///
/// The core's config string defines which file index and extensions are expected.
/// We look up the load info from the config based on the file extension.
pub fn send_rom(core: &mut MisterFpgaCore, rom_path: &Path) -> Result<()> {
    // Look up load info from the core config based on file extension
    let load_info = core
        .config()
        .load_info(rom_path)
        .map_err(|e| anyhow::anyhow!("Failed to get load info: {e}"))?;

    info!(
        "Sending ROM via FIO_FILE_TX (size: {} bytes)",
        std::fs::metadata(rom_path)
            .map(|m| m.len())
            .unwrap_or(0)
    );

    core.load_file(rom_path, load_info)
        .map_err(|e| anyhow::anyhow!("ROM transfer failed: {e}"))?;

    info!("ROM transfer complete");
    Ok(())
}
