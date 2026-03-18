mod analog;
mod bios;
mod button_remap;
mod cd_image;
mod core_settings;
mod hotkey;
mod input;
mod keyboard_map;
mod lifecycle;
mod neogeo;
mod neogeo_mame;
mod osd;
mod rom_transfer;
mod savestate;
mod sd_emu;
mod sram;
mod system_map;
mod video_audio;

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use std::path::PathBuf;
use tracing::{error, info};

#[derive(Parser)]
#[command(name = "mister-bridge", about = "MiSTer FPGA core bridge for REG-Linux")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Load and run a MiSTer FPGA core
    Run {
        /// REG-Linux system name (e.g. nes, snes, megadrive)
        #[arg(long)]
        system: Option<String>,

        /// Path to ROM file
        #[arg(long)]
        rom: Option<PathBuf>,

        /// Direct path to .rbf core file (alternative to --system)
        #[arg(long)]
        core: Option<PathBuf>,

        /// Directory containing MiSTer .rbf core files
        #[arg(long, default_value = "/userdata/bios/mister/cores")]
        cores_dir: PathBuf,

        /// Disk image to mount as SD card (format: "path" or "index:path", repeatable)
        #[arg(long = "disk")]
        disks: Vec<String>,

        /// BIOS file with explicit load index (format: "index:path", repeatable)
        #[arg(long = "bios")]
        bios_files: Vec<String>,

        /// Directory to auto-discover MiSTer-style boot ROMs (boot.rom, boot1.rom, ...)
        #[arg(long, default_value = "/userdata/bios/mister")]
        bios_dir: PathBuf,

        /// Directory for save state files
        #[arg(long, default_value = "/userdata/saves/mister")]
        saves_dir: PathBuf,

        /// Core status bit setting (repeatable, format: "start:end=value" or "bit=value")
        #[arg(long = "setting")]
        settings: Vec<String>,

        /// Audio volume (0-100, default: 100)
        #[arg(long, default_value = "100")]
        volume: u8,

        /// Force scandoubler for VGA output
        #[arg(long)]
        forced_scandoubler: bool,

        /// Use 96kHz HDMI audio (default: 48kHz)
        #[arg(long)]
        hdmi_audio_96k: bool,

        /// DVI mode (no audio over HDMI)
        #[arg(long)]
        dvi: bool,

        /// HDMI limited color range (0=full, 1=limited, 2=limited for VGA converters)
        #[arg(long, default_value = "0")]
        hdmi_limited: u8,

        /// Direct video output (active video timing over HDMI)
        #[arg(long)]
        direct_video: bool,

        /// Connect VGA output to scaler
        #[arg(long)]
        vga_scaler: bool,

        /// Enable composite sync on VGA output
        #[arg(long)]
        composite_sync: bool,

        /// Enable YPbPr component video output
        #[arg(long)]
        ypbpr: bool,

        /// Enable sync on green for VGA output
        #[arg(long)]
        vga_sog: bool,

        /// Video brightness (0-100, default: 50)
        #[arg(long, default_value = "50")]
        brightness: u8,

        /// Video contrast (0-100, default: 50)
        #[arg(long, default_value = "50")]
        contrast: u8,

        /// MiSTer.ini config file for persistent video/audio settings
        #[arg(long)]
        config: Option<PathBuf>,

        /// Custom aspect ratio (format: "H:V", e.g. "16:9", "4:3")
        #[arg(long)]
        custom_aspect_ratio: Option<String>,

        /// Directory for screenshots (Select+B)
        #[arg(long, default_value = "/userdata/screenshots/mister")]
        screenshots_dir: PathBuf,
    },

    /// List available MiSTer cores
    ListCores {
        /// Directory containing MiSTer .rbf core files
        #[arg(long, default_value = "/userdata/bios/mister/cores")]
        cores_dir: PathBuf,
    },

    /// Test FPGA connectivity
    TestFpga,
}

fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive(tracing::Level::INFO.into()),
        )
        .init();

    let cli = Cli::parse();

    match cli.command {
        Commands::Run {
            system,
            rom,
            core,
            cores_dir,
            disks,
            bios_files,
            bios_dir,
            saves_dir,
            settings,
            volume,
            forced_scandoubler,
            hdmi_audio_96k,
            dvi,
            hdmi_limited,
            direct_video,
            vga_scaler,
            composite_sync,
            ypbpr,
            vga_sog,
            brightness,
            contrast,
            config,
            custom_aspect_ratio,
            screenshots_dir,
        } => cmd_run(
            system, rom, core, cores_dir, disks, bios_files, bios_dir, saves_dir, settings,
            volume, forced_scandoubler, hdmi_audio_96k, dvi, hdmi_limited, direct_video,
            vga_scaler, composite_sync, ypbpr, vga_sog, brightness, contrast,
            config, custom_aspect_ratio, screenshots_dir,
        ),

        Commands::ListCores { cores_dir } => cmd_list_cores(&cores_dir),

        Commands::TestFpga => cmd_test_fpga(),
    }
}

fn cmd_run(
    system: Option<String>,
    rom: Option<PathBuf>,
    core: Option<PathBuf>,
    cores_dir: PathBuf,
    disks: Vec<String>,
    bios_files: Vec<String>,
    bios_dir: PathBuf,
    saves_dir: PathBuf,
    settings: Vec<String>,
    volume: u8,
    forced_scandoubler: bool,
    hdmi_audio_96k: bool,
    dvi: bool,
    hdmi_limited: u8,
    direct_video: bool,
    vga_scaler: bool,
    composite_sync: bool,
    ypbpr: bool,
    vga_sog: bool,
    brightness: u8,
    contrast: u8,
    config: Option<PathBuf>,
    custom_aspect_ratio: Option<String>,
    screenshots_dir: PathBuf,
) -> Result<()> {
    // Resolve the RBF path: either direct --core or lookup via --system
    let rbf_path = match core {
        Some(path) => {
            anyhow::ensure!(path.exists(), "Core file not found: {}", path.display());
            path
        }
        None => {
            let sys_name = system
                .as_deref()
                .context("Either --system or --core must be specified")?;
            system_map::find_core_rbf(sys_name, &cores_dir)
                .with_context(|| format!("No MiSTer core found for system '{sys_name}'"))?
        }
    };

    info!("Loading core: {}", rbf_path.display());

    // Initialize FPGA and load the core
    let mut fpga_core = lifecycle::load_core(&rbf_path)?;

    // Apply video/audio configuration (from config file + CLI overrides)
    video_audio::apply_video_audio(
        &mut fpga_core,
        volume,
        forced_scandoubler,
        hdmi_audio_96k,
        dvi,
        hdmi_limited,
        direct_video,
        vga_scaler,
        composite_sync,
        ypbpr,
        vga_sog,
        brightness,
        contrast,
        config.as_deref(),
        custom_aspect_ratio.as_deref(),
    )?;

    // Apply core settings if provided (supports both raw "5:8=3" and named "Region=Japan")
    if !settings.is_empty() {
        let resolved = core_settings::resolve_settings(&fpga_core, &settings)?;
        core_settings::apply_settings(&mut fpga_core, &resolved)?;
    }

    // Send BIOS files: explicit --bios args first, then auto-discovery
    let mut bios_entries: Vec<bios::BiosFile> = Vec::new();
    for arg in &bios_files {
        let (idx_str, path_str) = arg
            .split_once(':')
            .context("--bios format must be 'index:path'")?;
        let index: u8 = idx_str
            .parse()
            .with_context(|| format!("Invalid BIOS index: {idx_str}"))?;
        bios_entries.push(bios::BiosFile {
            index,
            path: PathBuf::from(path_str),
        });
    }
    // Auto-discover BIOS files if none explicitly provided
    if bios_entries.is_empty() {
        if let Some(sys) = system.as_deref() {
            let sys_bios_dir = bios_dir.join(sys);
            let search_dir = if sys_bios_dir.is_dir() {
                &sys_bios_dir
            } else {
                &bios_dir
            };
            bios_entries = bios::auto_discover_bios(&fpga_core, sys, search_dir);
        }
    }
    if !bios_entries.is_empty() {
        bios::send_bios_files(&mut fpga_core, &bios_entries)?;
    }

    // Transfer ROM if provided (skip .m3u playlists — used only for save state naming)
    if let Some(rom_path) = &rom {
        anyhow::ensure!(
            rom_path.exists(),
            "ROM file not found: {}",
            rom_path.display()
        );
        let ext = rom_path
            .extension()
            .and_then(|e| e.to_str())
            .unwrap_or("")
            .to_lowercase();
        if ext == "m3u" {
            // M3U playlist: disc images are mounted via --disk, ROM path is for save naming only
            info!("M3U playlist (save state naming): {}", rom_path.display());
        } else if rom_path.is_dir() {
            // Directory: treat as MAME/Darksoft NeoGeo ROM set
            info!("Loading NeoGeo MAME romset: {}", rom_path.display());
            neogeo_mame::load_mame_romset(&mut fpga_core, rom_path)?;
        } else if ext == "neo" {
            // NeoGeo .neo format: multi-section loading with sprite/fix conversion
            info!("Loading NeoGeo .neo file: {}", rom_path.display());
            neogeo::load_neo(&mut fpga_core, rom_path)?;
        } else {
            info!("Transferring ROM: {}", rom_path.display());
            rom_transfer::send_rom(&mut fpga_core, rom_path)?;
        }
    }

    // Mount SRAM save file if the core supports battery-backed saves
    if let Some(rom_path) = &rom {
        if let Some(sys) = system.as_deref() {
            if let Some(save_index) = sram::detect_save_support(&fpga_core, rom_path) {
                let sram_file = sram::sram_path(&saves_dir, sys, rom_path);
                if let Err(e) = sram::mount_sram(&mut fpga_core, &sram_file, save_index) {
                    error!("SRAM mount failed: {e:#}");
                }
            }
        }
    }

    // Parse and mount disk images, resolving CD image formats (CUE→BIN, CHD→temp)
    let mut disk_mounts: Vec<sd_emu::DiskMount> = Vec::new();
    let mut cd_images: Vec<cd_image::CdImage> = Vec::new();
    for (seq_idx, disk_arg) in disks.iter().enumerate() {
        // Format: "index:path" or just "path" (sequential index)
        let (index, raw_path) = if let Some((idx_str, path_str)) = disk_arg.split_once(':') {
            if let Ok(idx) = idx_str.parse::<u8>() {
                (idx, PathBuf::from(path_str))
            } else {
                // Not a valid index:path, treat whole string as path
                (seq_idx as u8, PathBuf::from(disk_arg))
            }
        } else {
            (seq_idx as u8, PathBuf::from(disk_arg))
        };
        // Resolve CD images: CUE→BIN file, CHD→decompressed temp file
        let resolved = cd_image::resolve_cd_image(&raw_path)?;
        let mount_path = resolved.path().to_path_buf();
        cd_images.push(resolved);
        disk_mounts.push(sd_emu::DiskMount { index, path: mount_path });
    }
    // Multi-disc detection: if multiple disks have sequential auto-assigned indices
    // (0, 1, 2...), this is a CD playlist — only mount the first disc.
    // Non-sequential indices (e.g. ao486: slot 0, 2, 4) mount all at their slots.
    let is_multi_disc = disk_mounts.len() > 1
        && disk_mounts
            .iter()
            .enumerate()
            .all(|(i, d)| d.index == i as u8);

    if is_multi_disc {
        anyhow::ensure!(disk_mounts.len() <= 6, "Maximum 6 disc images supported");
        sd_emu::mount_disks(&mut fpga_core, &disk_mounts[..1])?;
        info!(
            "Multi-disc playlist: {} discs, mounted disc 1 at slot 0",
            disk_mounts.len()
        );
    } else if !disk_mounts.is_empty() {
        anyhow::ensure!(disk_mounts.len() <= 6, "Maximum 6 disk images supported");
        sd_emu::mount_disks(&mut fpga_core, &disk_mounts)?;
    }

    // Determine the game path for save states: prefer --rom, fall back to first --disk
    let first_disk_path = disk_mounts.first().map(|d| d.path.clone());
    let game_path = rom.as_ref().or(first_disk_path.as_ref());

    // Build save context if we have system + game path
    let save_ctx = match (&system, game_path) {
        (Some(sys), Some(path)) => {
            savestate::autoload(&mut fpga_core, &saves_dir, path, sys)?;
            Some(input::SaveContext {
                save_dir: saves_dir.clone(),
                system: sys.clone(),
                rom: path.clone(),
            })
        }
        _ => None,
    };

    // Build disc context for multi-disc swapping (CD playlists only)
    let mut disc_ctx = if is_multi_disc {
        let disc_paths: Vec<_> = disk_mounts.iter().map(|d| d.path.clone()).collect();
        Some(input::DiscContext::new(disc_paths, 0))
    } else {
        None
    };

    info!("Core running. Select+Start=exit, L1/R1=save/load, DPad=slot, L2/R2=disc, Y=OSD, B=screenshot, X=reset");

    // Enter the main input loop (blocks until exit hotkey)
    if let Err(e) = input::run_input_loop(
        &mut fpga_core,
        save_ctx.as_ref(),
        disc_ctx.as_mut(),
        system.as_deref(),
        Some(&screenshots_dir),
    ) {
        error!("Input loop error: {e:#}");
    }

    // Autosave on exit if we have context
    if let (Some(sys), Some(path)) = (&system, game_path) {
        savestate::autosave(&mut fpga_core, &saves_dir, path, sys)?;
    }

    // Drain any pending SD card writes before shutdown
    for _ in 0..10 {
        match fpga_core.poll_mounts() {
            Ok(true) => continue,
            _ => break,
        }
    }

    // Cleanup
    info!("Shutting down FPGA core");
    lifecycle::cleanup(&mut fpga_core);

    Ok(())
}

fn cmd_list_cores(cores_dir: &PathBuf) -> Result<()> {
    let cores = system_map::list_available_cores(cores_dir)?;
    if cores.is_empty() {
        println!("No .rbf cores found in {}", cores_dir.display());
        println!("Place MiSTer core files (.rbf) in this directory.");
    } else {
        println!("Available MiSTer cores in {}:", cores_dir.display());
        for (system, path) in &cores {
            println!("  {system:<16} -> {}", path.display());
        }
    }
    Ok(())
}

fn cmd_test_fpga() -> Result<()> {
    info!("Testing FPGA connectivity...");

    match lifecycle::test_fpga() {
        Ok(()) => {
            println!("FPGA test PASSED:");
            println!("  /dev/mem access:    OK");
            println!("  SoC register mmap:  OK");
            println!("  FPGA manager:       OK");
            Ok(())
        }
        Err(e) => {
            println!("FPGA test FAILED: {e:#}");
            Err(e)
        }
    }
}
