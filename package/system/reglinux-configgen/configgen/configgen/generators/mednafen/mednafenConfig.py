from configgen.systemFiles import HOME
from utils.logger import get_logger

eslog = get_logger(__name__)

# Define paths for Mednafen configuration and binary
MEDNAFEN_CONFIG_DIR = HOME + "/.mednafen"
MEDNAFEN_CONFIG_PATH = MEDNAFEN_CONFIG_DIR + "/mednafen.cfg"
MEDNAFEN_BIN_PATH = "/usr/bin/mednafen"

# List of all supported emulation systems
SYSTEMS = [
    "apple2",
    "gb",
    "gba",
    "gg",
    "lynx",
    "md",
    "nes",
    "ngp",
    "pce",
    "pce_fast",
    "pcfx",
    "psx",
    "sasplay",
    "sms",
    "snes",
    "snes_faust",
    "ss",
    "ssfplay",
    "vb",
    "wswan",
]


def setMednafenConfig(cfgConfig):
    # Enable all systems and set fullscreen stretch for each
    for system in SYSTEMS:
        cfgConfig.write(f"{system}.enable 1\n")
        cfgConfig.write(f"{system}.stretch full\n")

    # Audio configuration
    cfgConfig.write("sound.driver sdl\n")  # Use SDL sound driver
    cfgConfig.write("sound 1\n")  # Enable sound output

    # Video configuration
    cfgConfig.write("video.fs 1\n")  # Enable fullscreen mode
    cfgConfig.write("video.fs.display -1\n")  # Use default display

    # System settings
    cfgConfig.write("filesys.path_firmware firmware\n")  # Firmware path
    cfgConfig.write("autosave 0\n")  # Disable auto-save states
    cfgConfig.write("cheats 0\n")  # Disable cheats by default
    cfgConfig.write("fps.autoenable 0\n")  # Disable FPS display by default

    # Keyboard shortcuts configuration
    key_bindings = {
        "exit": ("keyboard", "0x0", "69"),  # Exit emulator
        "fast_forward": ("keyboard", "0x0", "53"),  # Fast forward
        "state_rewind": ("keyboard", "0x0", "42"),  # Rewind state
        "reset": ("keyboard", "0x0", "67"),  # Reset system
        "rotate_screen": ("keyboard", "0x0", "18+alt"),  # Rotate screen
    }

    # Write all key bindings to config
    for command, (device, id, key) in key_bindings.items():
        cfgConfig.write(f"command.{command} {device} {id} {key}\n")
