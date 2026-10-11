use anyhow::Result;
use mister_fpga::core::file::SdCard;
use mister_fpga::core::MisterFpgaCore;
use std::path::PathBuf;
use tracing::{debug, info};

/// A disk image to mount with an explicit slot index.
pub struct DiskMount {
    pub index: u8,
    pub path: PathBuf,
}

/// Mount disk images as SD cards on the FPGA core.
///
/// Each entry specifies an explicit mount index matching the core's S-section slots.
/// For example, ao486 uses: 0=Floppy A, 1=Floppy B, 2=IDE 0-0, 3=IDE 0-1, 4=IDE 1-0.
pub fn mount_disks(core: &mut MisterFpgaCore, disks: &[DiskMount]) -> Result<()> {
    for disk in disks {
        anyhow::ensure!(
            disk.path.exists(),
            "Disk image not found: {}",
            disk.path.display()
        );
        let card = SdCard::from_path(&disk.path).map_err(|e| {
            anyhow::anyhow!("Failed to open disk image {}: {e}", disk.path.display())
        })?;
        info!(
            "Mounting disk image {} at slot {}",
            disk.path.display(),
            disk.index
        );
        core.mount(card, disk.index)
            .map_err(|e| anyhow::anyhow!("Failed to mount disk image: {e}"))?;
    }
    Ok(())
}

/// Poll the FPGA core for SD card read/write requests and serve them.
///
/// This function should be called each iteration of the main input loop.
/// Returns Ok(()) even when no SD cards are mounted (no-op).
pub fn poll_sd(core: &mut MisterFpgaCore) -> Result<()> {
    match core.poll_mounts() {
        Ok(had_activity) => {
            if had_activity {
                debug!("SD card I/O serviced");
            }
            Ok(())
        }
        Err(e) => {
            debug!("SD poll error (non-fatal): {e}");
            Ok(())
        }
    }
}
