from configparser import ConfigParser
from os import makedirs, path
from typing import Any

from .hatariConfig import HATARI_CONFIG_DIR, HATARI_CONFIG_PATH


@staticmethod
def setHatariControllers(system: Any, playersControllers: Any) -> None:
    config = ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    config.optionxform = lambda optionstr: str(optionstr)

    padMapping = {1: "y", 2: "b", 3: "a"}

    if not path.exists(HATARI_CONFIG_DIR):
        makedirs(HATARI_CONFIG_DIR)

    if path.isfile(HATARI_CONFIG_PATH):
        config.read(HATARI_CONFIG_PATH)

    # pads
    # disable previous configuration
    for i in range(1, 6):  # 1 to 5 included
        section = "Joystick" + str(i)
        if config.has_section(section):
            config.set(section, "nJoyId", "-1")
            config.set(section, "nJoystickMode", "0")

    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        if nplayer <= 5:
            section = "Joystick" + str(nplayer)
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, "nJoyId", str(pad.index))
            config.set(section, "nJoystickMode", "1")

            if padMapping[1] in pad.inputs:
                config.set(section, "nButton1", str(pad.inputs[padMapping[1]].id))
            else:
                config.set(section, "nButton1", "0")
            if padMapping[2] in pad.inputs:
                config.set(section, "nButton2", str(pad.inputs[padMapping[2]].id))
            else:
                config.set(section, "nButton2", "1")
            if padMapping[3] in pad.inputs:
                config.set(section, "nButton3", str(pad.inputs[padMapping[3]].id))
            else:
                config.set(section, "nButton3", "2")
        nplayer += 1

    # Log
    if not config.has_section("Log"):
        config.add_section("Log")
    config.set("Log", "bConfirmQuit", "FALSE")

    # Screen
    if not config.has_section("Screen"):
        config.add_section("Screen")
    if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
        config.set("Screen", "bShowStatusbar", "TRUE")
    else:
        config.set("Screen", "bShowStatusbar", "FALSE")

    with open(HATARI_CONFIG_PATH, "w") as configfile:
        config.write(configfile)
