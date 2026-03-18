"""MiSTer FPGA generator for REG-Linux.

Generates command-line arguments for the mister-bridge utility to launch
MiSTer FPGA cores with appropriate BIOS, disk, and configuration settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from configgen.config.paths import BIOS, SAVES
from configgen.core import Command
from configgen.generators.generator import DeviceConfig, Generator

if TYPE_CHECKING:
    from typing import Any

    from configgen.core import Emulator

MISTER_BRIDGE_BIN: str = "/usr/bin/mister-bridge"
MISTER_CORES_DIR: str = str(BIOS / "mister/cores")
MISTER_SAVES_DIR: str = str(SAVES / "mister")
MISTER_BIOS_DIR: str = str(BIOS)
MISTER_DISKS_DIR: str = str(BIOS / "mister")

# Systems where the ROM (CD image) should be mounted as a disk
# instead of transferred via ROM protocol
CD_SYSTEMS: frozenset[str] = frozenset({
    "segacd",
    "pcenginecd",
    "psx",
    "saturn",
    "cdi",
    "pcfx",
})

# Systems where the "ROM" is actually a disk image to mount (not transfer via SPI)
# Maps system -> default mount slot index for the game file
# (dos overrides per-extension via _dos_disk_index)
DISK_GAME_SYSTEMS: dict[str, int] = {
    "dos": 2,  # ao486: IDE 0-0 (primary master HDD)
    "x68000": 0,  # X68000: FDD0 (D88 floppy images)
    "pc88": 0,  # PC-8801: FDD0 (D88 floppy images)
    "archimedes": 0,  # Archimedes: floppy 0 (ADF images)
    "amiga": 0,  # Amiga: DF0: (ADF floppy images)
    "amiga500": 0,  # Amiga 500: DF0:
    "amiga1200": 0,  # Amiga 1200: DF0:
    "macintosh": 0,  # MacPlus: floppy 0 (DSK images)
    "pcxt": 0,  # PC/XT: floppy A (IMG images)
    "oric": 0,  # Oric: disk 0 (DSK images)
}

# ao486 config string mount slots:
#   S0 = Floppy A (IMG/IMA/VFD)
#   S1 = Floppy B (IMG/IMA/VFD)
#   S2 = IDE 0-0 (VHD) — primary boot HDD
#   S3 = IDE 0-1 (VHD)
#   S4 = IDE 1-0 (VHD/ISO/CUE/CHD) — CD-ROM
#   S5 = IDE 1-1 (VHD/ISO/CUE/CHD)

# Per-system default core settings (named, resolved at runtime against core config).
# These provide sensible defaults; user can override via mister_settings in system.conf.
# Named settings are matched case-insensitively against the core's OSD menu options.
MISTER_DEFAULTS: dict[str, list[str]] = {
    "neogeo": [
        "System Type=Console(AES)",  # AES mode for home console ROMs
    ],
    "n64": [
        "Expansion Pak=On",  # Many games require the Expansion Pak
    ],
    "zxspectrum": [
        "Memory=128K",  # 128K covers most software
    ],
    "amstradcpc": [
        "Model=6128",  # 128KB model for broader compatibility
    ],
    "atarist": [
        "Memory=4MB",  # More memory for game/demo compatibility
        "Chipset=STE",  # STE adds blitter and DMA audio
    ],
    "dos": [
        "CPU Speed=Max",  # Maximum CPU speed for ao486
    ],
    "pcxt": [
        "CPU Speed=Max",  # Maximum CPU speed for PCXT
    ],
    "c128": [
        "Model=C128",  # C128 mode (vs C64 compatibility mode)
    ],
    "archimedes": [
        "CPU Speed=Max",  # Maximum CPU speed for Archimedes
    ],
}

# BIOS file entry: (filename, load_index)
BiosEntry = tuple[str, int]

# Per-system BIOS file mapping: system -> [(filename, load_index), ...]
# These map REG-Linux standard BIOS names to MiSTer core F-section indices.
# Files are searched in /userdata/bios/<system>/ then /userdata/bios/
# Note: Alternative BIOS names sharing the same index are fallbacks, not additional files.
BIOS_MAP: dict[str, list[BiosEntry]] = {
    "psx": [
        ("scph5501.bin", 0),  # US BIOS → boot.rom
        ("scph5500.bin", 1),  # JP BIOS → boot1.rom
        ("scph5502.bin", 2),  # EU BIOS → boot2.rom
    ],
    "gba": [
        ("gba_bios.bin", 0),
    ],
    "fds": [
        ("disksys.rom", 0),
    ],
    "saturn": [
        ("saturn_bios.bin", 0),
        ("sega_101.bin", 0),  # Alternative name (same index = fallback)
    ],
    "colecovision": [
        ("colecovision.rom", 0),
    ],
    "intellivision": [
        ("exec.bin", 0),
        ("grom.bin", 1),
    ],
    "atari5200": [
        ("ATARIXL.ROM", 0),
        ("5200.rom", 0),  # Alternative name (same index = fallback)
    ],
    "atari800": [
        ("ATARIXL.ROM", 0),
        ("ATARIBAS.ROM", 1),
    ],
    "lynx": [
        ("lynxboot.img", 0),
    ],
    "ti99": [
        ("994aROM.Bin", 0),
        ("994aGROM.Bin", 1),
    ],
    "coco": [
        ("coco3.rom", 0),
        ("disk11.rom", 1),
    ],
    "dos": [
        ("ao486/boot0.rom", 0),  # ao486 system BIOS
        ("ao486/boot1.rom", 1),  # ao486 VGA BIOS
    ],
    "macintosh": [
        ("MacPlus.rom", 0),
    ],
    "pcxt": [
        ("pcxt/boot0.rom", 0),  # PC/XT BIOS
    ],
    "cdi": [
        ("cdi/zx405042p.rom", 0),  # CD-i BIOS
        ("cdi/cdi200.rom", 0),  # Alternative name (same index = fallback)
    ],
    "x68000": [
        ("x68000/iplrom.dat", 0),  # X68000 IPL ROM
        ("x68000/cgrom.dat", 1),  # X68000 CG ROM
    ],
    "pc88": [
        ("pc88/N88.ROM", 0),  # PC-8801 N88-BASIC ROM
    ],
    "archimedes": [
        ("archimedes/riscos.rom", 0),  # Archimedes RISC OS ROM
    ],
    "colecoadam": [
        ("colecovision.rom", 0),
    ],
    "pcfx": [
        ("pcfx/pcfx.rom", 0),
    ],
    "jaguar": [
        ("jaguar/jagboot.rom", 0),
    ],
}


def _find_bios(system_name: str) -> list[tuple[int, str]]:
    """Find BIOS files for a system.

    Searches for BIOS files in system-specific subdirectory first,
    then falls back to the global BIOS directory.

    Args:
        system_name: The system identifier (e.g., "psx", "gba").

    Returns:
        List of (index, path) pairs for found BIOS files.
        Multiple BIOS files with different indices can be returned.
        Alternative names sharing the same index are treated as fallbacks.

    """
    entries = BIOS_MAP.get(system_name, [])
    if not entries:
        return []

    result: list[tuple[int, str]] = []
    found_indices: set[int] = set()

    for filename, index in entries:
        # Skip if we already found a BIOS for this index (alternative names are fallbacks)
        if index in found_indices:
            continue

        # Search in system-specific subdir first, then global bios dir
        search_dirs = [Path(MISTER_BIOS_DIR) / system_name, Path(MISTER_BIOS_DIR)]
        for search_dir in search_dirs:
            candidate = search_dir / filename
            if candidate.is_file():
                result.append((index, str(candidate)))
                found_indices.add(index)
                break

    return result


def _parse_m3u(m3u_path: str) -> list[str]:
    """Parse an .m3u playlist file and return a list of absolute disc image paths.

    Args:
        m3u_path: Path to the .m3u playlist file.

    Returns:
        List of absolute paths to disc images referenced in the playlist.

    """
    m3u = Path(m3u_path)
    parent = m3u.parent
    discs: list[str] = []
    try:
        for line in m3u.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            disc_path = Path(line)
            if not disc_path.is_absolute():
                disc_path = parent / disc_path
            if disc_path.is_file():
                discs.append(str(disc_path))
    except OSError:
        pass
    return discs


def _dos_disk_index(rom_path: str) -> int:
    """Determine the ao486 mount slot index based on file extension.

    ao486 config string slots:
        S0/S1 = Floppy A/B (IMG, IMA, VFD)
        S2/S3 = IDE 0-0/0-1 (VHD) — primary HDD
        S4/S5 = IDE 1-0/1-1 (VHD, ISO, CUE, CHD) — CD-ROM

    Args:
        rom_path: Path to the ROM/disk image file.

    Returns:
        Slot index (0=floppy A, 2=IDE primary HDD, 4=CD-ROM).

    """
    ext = Path(rom_path).suffix.lower()
    if ext in {".img", ".ima", ".vfd"}:
        return 0  # Floppy A:
    if ext in {".iso", ".cue", ".chd"}:
        return 4  # IDE 1-0 (CD-ROM)
    return 2  # IDE 0-0 (primary HDD) — default for .vhd and others


class MisterGenerator(Generator):
    """MiSTer FPGA generator for REG-Linux.

    Generates command-line arguments for the mister-bridge utility to launch
    MiSTer FPGA cores with appropriate BIOS, disk, and configuration settings.
    """

    def generate(
        self,
        system: Emulator,
        rom: str,
        players_controllers: dict[str, Any],
        metadata: dict[str, Any],
        guns: DeviceConfig,
        wheels: DeviceConfig,
        game_resolution: dict[str, Any],
    ) -> Command:
        """Generate the command to launch the MiSTer FPGA core.

        Args:
            system: The Emulator instance with its configurations.
            rom: Path to the ROM file to launch.
            players_controllers: Controller configurations for players.
            metadata: Game metadata.
            guns: Light gun configurations.
            wheels: Racing wheel configurations.
            game_resolution: Game resolution settings.

        Returns:
            Command object with the mister-bridge command and arguments.

        """
        command_array: list[str] = [
            MISTER_BRIDGE_BIN,
            "run",
            "--system",
            system.name,
            "--cores-dir",
            MISTER_CORES_DIR,
            "--saves-dir",
            MISTER_SAVES_DIR,
            "--bios-dir",
            MISTER_BIOS_DIR,
        ]

        # Pass explicit BIOS files from our mapping table
        for index, bios_path in _find_bios(system.name):
            command_array.extend(["--bios", f"{index}:{bios_path}"])

        # Determine how to pass the game file
        if system.name in DISK_GAME_SYSTEMS:
            # Disk-based system: mount at the system-specific slot index
            slot = (
                _dos_disk_index(rom)
                if system.name == "dos"
                else DISK_GAME_SYSTEMS[system.name]
            )
            command_array.extend(["--disk", f"{slot}:{rom}"])
        elif system.name in CD_SYSTEMS:
            # CD-based system: mount as disk(s)
            # .m3u playlists expand to multiple --disk args for multi-disc support
            if Path(rom).suffix.lower() == ".m3u":
                discs = _parse_m3u(rom)
                if discs:
                    # Use .m3u path as --rom for save state naming
                    command_array.extend(["--rom", rom])
                    for disc in discs:
                        command_array.extend(["--disk", disc])
                else:
                    command_array.extend(["--disk", rom])
            else:
                command_array.extend(["--disk", rom])
        else:
            # Cartridge system: transfer via ROM protocol
            command_array.extend(["--rom", rom])

        # Auto-detect additional disk images from bios/mister/<system> directory
        disks_dir = Path(MISTER_DISKS_DIR) / system.name
        if disks_dir.is_dir():
            for img in sorted(disks_dir.iterdir()):
                if img.suffix.lower() in {".img", ".vhd", ".hdd", ".iso", ".chd"}:
                    img_str = str(img)
                    if system.name == "dos":
                        # For ao486, mount additional disks at the right slot
                        idx = _dos_disk_index(img_str)
                        command_array.extend(["--disk", f"{idx}:{img_str}"])
                    else:
                        command_array.extend(["--disk", img_str])

        # Apply per-system default settings (can be overridden by mister_settings)
        for setting in MISTER_DEFAULTS.get(system.name, []):
            command_array.extend(["--setting", setting])

        # Per-game/system core settings (status bit overrides)
        # Format in system.conf: mister_settings = "5:8=3,10=1"
        # These are applied AFTER defaults so they take precedence.
        if system.isOptSet("mister_settings"):
            for setting in system.config["mister_settings"].split(","):
                setting = setting.strip()
                if setting:
                    command_array.extend(["--setting", setting])

        # Custom aspect ratio (format: "H:V", e.g. "16:9", "4:3")
        if system.isOptSet("mister_aspect_ratio"):
            command_array.extend([
                "--custom-aspect-ratio",
                system.config["mister_aspect_ratio"],
            ])

        # Video brightness/contrast (0-100, default 50=neutral)
        if system.isOptSet("mister_brightness"):
            command_array.extend(["--brightness", system.config["mister_brightness"]])
        if system.isOptSet("mister_contrast"):
            command_array.extend(["--contrast", system.config["mister_contrast"]])

        # VGA output options
        if system.getOptBoolean("mister_vga_scaler"):
            command_array.append("--vga-scaler")
        if system.getOptBoolean("mister_ypbpr"):
            command_array.append("--ypbpr")

        # MiSTer.ini config file for advanced video/audio settings
        if system.isOptSet("mister_config"):
            command_array.extend(["--config", system.config["mister_config"]])

        return Command(array=command_array)
