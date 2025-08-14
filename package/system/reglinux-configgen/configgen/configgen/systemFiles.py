# Paths used throughout the REG-Linux system for configurations, assets, and user data

# Default system configuration path (read-only base)
HOME_INIT = '/usr/share/reglinux/datainit/system/'

# Writable user system path
HOME = '/userdata/system'

# Configuration directories
CONF_INIT = HOME_INIT + '/configs'  # Initial config files (read-only)
CONF = HOME + '/configs'            # User config files (writable)

# Standard user media and data directories
SCREENSHOTS = '/userdata/screenshots'  # Directory to save screenshots
RECORDINGS = '/userdata/recordings'    # Directory to save video recordings
BIOS = '/userdata/bios'                # BIOS files directory (used by emulators)
OVERLAYS = '/userdata/overlays'        # Overlay images directory (custom visuals/UI)
ROMS = '/userdata/roms'                # Game ROMs directory
SAVES = '/userdata/saves/'             # Save files directory
CHEATS = '/userdata/cheats'            # Game Cheats diretory

# EmulationStation related configuration files and metadata
ES_SETTINGS = CONF + '/emulationstation/es_settings.cfg'  # Main ES settings file
ES_GUNS_METADATA = '/usr/share/emulationstation/resources/gungames.xml'   # Metadata for lightgun-compatible games
ES_WHEELS_METADATA = '/usr/share/emulationstation/resources/wheelgames.xml'  # Metadata for wheel-compatible games
ES_GAMES_METADATA = '/usr/share/emulationstation/resources/gamesdb.xml'   # General games database metadata

# Global system configuration and logs
SYSTEM_CONF = HOME + '/system.conf'  # System-wide configuration file
LOGDIR = HOME + '/logs/'             # Directory where log files are stored

# Overlay decoration paths
OVERLAY_SYSTEM = '/usr/share/reglinux/datainit/decorations'  # Default overlays (read-only)
OVERLAY_USER = '/userdata/decorations'                       # Custom user overlays
OVERLAY_CONFIG_FILE = '/userdata/system/configs/retroarch/overlay.cfg'  # RetroArch overlay config
