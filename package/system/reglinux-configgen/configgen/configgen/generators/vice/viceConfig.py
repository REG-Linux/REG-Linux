from configgen.settings import UnixSettings
from configgen.systemFiles import CONF
import os

VICE_CONFIG_DIR = CONF + "/vice"
VICE_CONFIG_PATH = VICE_CONFIG_DIR + "/sdl-vicerc"
VICE_CONTROLLER_PATH = VICE_CONFIG_DIR + "/sdl-joymap.vjm"
VICE_BIN_DIR = "/usr/bin/"


def setViceConfig(system, metadata, guns):
    # Create directory if it doesn't exist
    os.makedirs(VICE_CONFIG_DIR, exist_ok=True)

    viceConfig = UnixSettings(VICE_CONFIG_PATH)

    # Ensure the Version section exists and set the ConfigVersion
    viceConfig.ensure_section("Version")
    viceConfig.set("Version", "ConfigVersion", "3.9")

    if system.config["core"] == "x64":
        systemCore = "C64"
    elif system.config["core"] == "x64dtv":
        systemCore = "C64DTV"
    elif system.config["core"] == "xplus4":
        systemCore = "PLUS4"
    elif system.config["core"] == "xscpu64":
        systemCore = "SCPU64"
    elif system.config["core"] == "xvic":
        systemCore = "VIC20"
    elif system.config["core"] == "xpet":
        systemCore = "PET"
    else:
        systemCore = "C128"

    viceConfig.ensure_section(systemCore)

    viceConfig.set(systemCore, "SaveResourcesOnExit", "0")
    viceConfig.set(systemCore, "SoundDeviceName", "alsa")

    if system.isOptSet("noborder") and system.getOptBoolean("noborder") == True:
        viceConfig.set(systemCore, "SDLGLAspectMode", "0")
        viceConfig.set(systemCore, "VICBorderMode", "3")
    else:
        viceConfig.set(systemCore, "SDLGLAspectMode", "2")
        viceConfig.set(systemCore, "VICBorderMode", "0")
    viceConfig.set(systemCore, "VICFullscreen", "1")
    if (
        system.isOptSet("use_guns")
        and system.getOptBoolean("use_guns")
        and len(guns) >= 1
    ):
        if "gun_type" in metadata and metadata["gun_type"] == "stack_light_rifle":
            viceConfig.set(systemCore, "JoyPort1Device", "15")
        else:
            viceConfig.set(systemCore, "JoyPort1Device", "14")
    else:
        viceConfig.set(systemCore, "JoyPort1Device", "1")
    viceConfig.set(systemCore, "JoyDevice1", "4")
    if not systemCore == "VIC20":
        viceConfig.set(systemCore, "JoyDevice2", "4")
    viceConfig.set(systemCore, "JoyMapFile", VICE_CONTROLLER_PATH)

    # custom : allow the user to configure directly sdl-vicerc via system.conf via lines like : vice.section.option=value
    for user_config in system.config:
        if user_config[:5] == "vice.":
            section_option = user_config[5:]
            section_option_splitter = section_option.find(".")
            custom_section = section_option[:section_option_splitter]
            custom_option = section_option[section_option_splitter + 1 :]
            viceConfig.ensure_section(custom_section)
            viceConfig.set(custom_section, custom_option, system.config[user_config])

    # update the configuration file
    viceConfig.write()
