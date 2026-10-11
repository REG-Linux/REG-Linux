use anyhow::{Context, Result};
use mister_fpga::core::MisterFpgaCore;
use mister_fpga::fpga::MisterFpga;
use std::fs;
use std::path::Path;
use tracing::info;

/// Initialize the FPGA hardware, load an RBF bitstream, and return a ready core.
pub fn load_core(rbf_path: &Path) -> Result<MisterFpgaCore> {
    let rbf_bytes = fs::read(rbf_path)
        .with_context(|| format!("Failed to read RBF file: {}", rbf_path.display()))?;

    info!("Initializing FPGA hardware");
    let mut fpga = MisterFpga::init().map_err(|e| anyhow::anyhow!("FPGA init failed: {e}"))?;

    info!("Loading RBF bitstream ({} bytes)", rbf_bytes.len());
    fpga.load(&rbf_bytes[..])
        .map_err(|e| anyhow::anyhow!("RBF load failed: {e:?}"))?;

    fpga.wait_for_ready();

    info!("Creating core interface");
    let mut core =
        MisterFpgaCore::new(fpga).map_err(|e| anyhow::anyhow!("Core init failed: {e}"))?;

    // Read and log the config string
    let config = core.config();
    info!("Core name: {}", config.name);

    // Send initial RTC
    core.send_rtc()
        .map_err(|e| anyhow::anyhow!("RTC send failed: {e}"))?;

    Ok(core)
}

/// Cleanup: reset core state.
pub fn cleanup(core: &mut MisterFpgaCore) {
    core.soft_reset();
}

/// Test basic FPGA hardware access without loading a core.
pub fn test_fpga() -> Result<()> {
    info!("Opening /dev/mem and mapping SoC registers");
    let fpga = MisterFpga::init().map_err(|e| anyhow::anyhow!("FPGA init failed: {e}"))?;

    info!("FPGA ready: {}", fpga.is_ready());
    Ok(())
}
