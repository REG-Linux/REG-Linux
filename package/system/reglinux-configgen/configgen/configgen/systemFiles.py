"""Paths used throughout the REG-Linux system for configurations, assets, and user data."""

from pathlib import Path
from typing import Final

# Default system configuration path (read-only base)
HOME_INIT: Final[Path] = Path("/usr/share/reglinux/datainit/system")

# Writable user system path
HOME: Final[Path] = Path("/userdata/system")

# Configuration directories
CONF_INIT: Final[Path] = HOME_INIT / "configs"  # Initial config files (read-only)
CONF: Final[Path] = HOME / "configs"  # User config files (writable)

# Standard user media and data directories
SCREENSHOTS: Final[Path] = Path(
    "/userdata/screenshots",
)  # Directory to save screenshots
RECORDINGS: Final[Path] = Path(
    "/userdata/recordings",
)  # Directory to save video recordings
BIOS: Final[Path] = Path("/userdata/bios")  # BIOS files directory (used by emulators)
OVERLAYS: Final[Path] = Path(
    "/userdata/overlays",
)  # Overlay images directory (custom visuals/UI)
ROMS: Final[Path] = Path("/userdata/roms")  # Game ROMs directory
SAVES: Final[Path] = Path("/userdata/saves")  # Save files directory
CHEATS: Final[Path] = Path("/userdata/cheats")  # Game Cheats directory

# EmulationStation related configuration files and metadata
ES_SETTINGS: Final[Path] = (
    CONF / "emulationstation" / "es_settings.cfg"
)  # Main ES settings file
ES_GUNS_METADATA: Final[Path] = Path(
    "/usr/share/emulationstation/resources/gungames.xml",
)  # Metadata for lightgun-compatible games
ES_WHEELS_METADATA: Final[Path] = Path(
    "/usr/share/emulationstation/resources/wheelgames.xml",
)  # Metadata for wheel-compatible games
ES_GAMES_METADATA: Final[Path] = Path(
    "/usr/share/emulationstation/resources/gamesdb.xml",
)  # General games database metadata

# Global system configuration and logs
SYSTEM_CONF: Final[Path] = HOME / "system.conf"  # System-wide configuration file
LOGDIR: Final[Path] = HOME / "logs"  # Directory where log files are stored

# Overlay decoration paths
OVERLAY_SYSTEM: Final[Path] = Path(
    "/usr/share/reglinux/datainit/decorations",
)  # Default overlays (read-only)
OVERLAY_USER: Final[Path] = Path("/userdata/decorations")  # Custom user overlays
OVERLAY_CONFIG_FILE: Final[Path] = Path(
    "/userdata/system/configs/retroarch/overlay.cfg",
)  # RetroArch overlay config
