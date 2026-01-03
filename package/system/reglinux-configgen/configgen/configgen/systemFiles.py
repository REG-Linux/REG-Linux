"""Paths used throughout the REG-Linux system for configurations, assets, and user data."""

from pathlib import Path

# Default system configuration path (read-only base)
HOME_INIT = Path("/usr/share/reglinux/datainit/system")

# Writable user system path
HOME = Path("/userdata/system")

# Configuration directories
CONF_INIT = HOME_INIT / "configs"  # Initial config files (read-only)
CONF = HOME / "configs"  # User config files (writable)

# Standard user media and data directories
SCREENSHOTS = Path("/userdata/screenshots")  # Directory to save screenshots
RECORDINGS = Path("/userdata/recordings")  # Directory to save video recordings
BIOS = Path("/userdata/bios")  # BIOS files directory (used by emulators)
OVERLAYS = Path("/userdata/overlays")  # Overlay images directory (custom visuals/UI)
ROMS = Path("/userdata/roms")  # Game ROMs directory
SAVES = Path("/userdata/saves")  # Save files directory
CHEATS = Path("/userdata/cheats")  # Game Cheats directory

# EmulationStation related configuration files and metadata
ES_SETTINGS = CONF / "emulationstation" / "es_settings.cfg"  # Main ES settings file
ES_GUNS_METADATA = Path(
    "/usr/share/emulationstation/resources/gungames.xml",
)  # Metadata for lightgun-compatible games
ES_WHEELS_METADATA = Path(
    "/usr/share/emulationstation/resources/wheelgames.xml",
)  # Metadata for wheel-compatible games
ES_GAMES_METADATA = Path(
    "/usr/share/emulationstation/resources/gamesdb.xml",
)  # General games database metadata

# Global system configuration and logs
SYSTEM_CONF = HOME / "system.conf"  # System-wide configuration file
LOGDIR = HOME / "logs"  # Directory where log files are stored

# Overlay decoration paths
OVERLAY_SYSTEM = Path(
    "/usr/share/reglinux/datainit/decorations",
)  # Default overlays (read-only)
OVERLAY_USER = Path("/userdata/decorations")  # Custom user overlays
OVERLAY_CONFIG_FILE = Path(
    "/userdata/system/configs/retroarch/overlay.cfg",
)  # RetroArch overlay config
