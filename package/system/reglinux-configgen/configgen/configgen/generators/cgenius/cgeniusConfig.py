from configgen.systemFiles import CONF, ROMS
from typing import Any

CGENIUS_CONFIG_DIR = CONF + "/cgenius"
CGENIUS_ROMS_DIR = ROMS + "/cgenius/"
CGENIUS_CONFIG_PATH = CGENIUS_CONFIG_DIR + "/cgenius.cfg"
CGENIUS_BIN_PATH = "/usr/bin/CGeniusExe"


def setCgeniusConfig(cgeniusConfig: Any, system: Any) -> None:
    # Now setup the options we want...
    if "FileHandling" not in cgeniusConfig:
        cgeniusConfig["FileHandling"] = {}

    cgeniusConfig["FileHandling"]["EnableLogfile"] = "false"
    cgeniusConfig["FileHandling"]["SearchPath1"] = CGENIUS_ROMS_DIR
    cgeniusConfig["FileHandling"]["SearchPath2"] = CGENIUS_ROMS_DIR + "games"

    if "Video" not in cgeniusConfig:
        cgeniusConfig["Video"] = {}
    # aspect
    if system.isOptSet("cgenius_aspect"):
        cgeniusConfig["Video"]["aspect"] = system.config["cgenius_aspect"]
    else:
        cgeniusConfig["Video"]["aspect"] = "4:3"
    # we always want fullscreen
    cgeniusConfig["Video"]["fullscreen"] = "true"
    # filter
    if system.isOptSet("cgenius_filter"):
        cgeniusConfig["Video"]["filter"] = system.config["cgenius_filter"]
    else:
        cgeniusConfig["Video"]["filter"] = "none"
    # quality
    if system.isOptSet("cgenius_quality"):
        cgeniusConfig["Video"]["OGLfilter"] = system.config["cgenius_quality"]
    else:
        cgeniusConfig["Video"]["OGLfilter"] = "nearest"
    # render resolution
    if system.isOptSet("cgenius_render"):
        if system.config["cgenius_render"] == "200":
            cgeniusConfig["Video"]["gameHeight"] = "200"
            cgeniusConfig["Video"]["gameWidth"] = "320"
        if system.config["cgenius_render"] == "240":
            cgeniusConfig["Video"]["gameHeight"] = "240"
            cgeniusConfig["Video"]["gameWidth"] = "320"
        if system.config["cgenius_render"] == "360":
            cgeniusConfig["Video"]["gameHeight"] = "360"
            cgeniusConfig["Video"]["gameWidth"] = "640"
        if system.config["cgenius_render"] == "480":
            cgeniusConfig["Video"]["gameHeight"] = "480"
            cgeniusConfig["Video"]["gameWidth"] = "640"
    else:
        cgeniusConfig["Video"]["gameHeight"] = "200"
        cgeniusConfig["Video"]["gameWidth"] = "320"
    # mouse
    if system.isOptSet("cgenius_cursor"):
        cgeniusConfig["Video"]["ShowCursor"] = system.config["cgenius_cursor"]
    else:
        cgeniusConfig["Video"]["ShowCursor"] = "false"


# Show mouse on screen for the Config Screen
def getMouseMode(config: Any, rom: str) -> bool:
    return True
