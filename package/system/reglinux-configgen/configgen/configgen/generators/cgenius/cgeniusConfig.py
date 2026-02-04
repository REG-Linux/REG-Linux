from pathlib import Path
from typing import Any

from configgen.systemFiles import CONF, ROMS

CGENIUS_CONFIG_DIR = str(Path(CONF) / "cgenius")
CGENIUS_ROMS_DIR = str(Path(ROMS) / "cgenius" / "")
CGENIUS_CONFIG_PATH = str(Path(CGENIUS_CONFIG_DIR) / "cgenius.cfg")
CGENIUS_BIN_PATH = "/usr/bin/CGeniusExe"


def setCgeniusConfig(cgeniusConfig: Any, system: Any) -> None:
    # Now setup the options we want...
    # Ensure sections exist
    if not cgeniusConfig.has_section("FileHandling"):
        cgeniusConfig.add_section("FileHandling")

    cgeniusConfig.set("FileHandling", "EnableLogfile", "false")
    cgeniusConfig.set("FileHandling", "SearchPath1", CGENIUS_ROMS_DIR)
    cgeniusConfig.set(
        "FileHandling",
        "SearchPath2",
        str(Path(CGENIUS_ROMS_DIR) / "games"),
    )

    if not cgeniusConfig.has_section("Video"):
        cgeniusConfig.add_section("Video")

    # aspect
    if system.isOptSet("cgenius_aspect"):
        cgeniusConfig.set("Video", "aspect", system.config["cgenius_aspect"])
    else:
        cgeniusConfig.set("Video", "aspect", "4:3")
    # we always want fullscreen
    cgeniusConfig.set("Video", "fullscreen", "true")
    # filter
    if system.isOptSet("cgenius_filter"):
        cgeniusConfig.set("Video", "filter", system.config["cgenius_filter"])
    else:
        cgeniusConfig.set("Video", "filter", "none")
    # quality
    if system.isOptSet("cgenius_quality"):
        cgeniusConfig.set("Video", "OGLfilter", system.config["cgenius_quality"])
    else:
        cgeniusConfig.set("Video", "OGLfilter", "nearest")
    # render resolution
    if system.isOptSet("cgenius_render"):
        if system.config["cgenius_render"] == "200":
            cgeniusConfig.set("Video", "gameHeight", "200")
            cgeniusConfig.set("Video", "gameWidth", "320")
        if system.config["cgenius_render"] == "240":
            cgeniusConfig.set("Video", "gameHeight", "240")
            cgeniusConfig.set("Video", "gameWidth", "320")
        if system.config["cgenius_render"] == "360":
            cgeniusConfig.set("Video", "gameHeight", "360")
            cgeniusConfig.set("Video", "gameWidth", "640")
        if system.config["cgenius_render"] == "480":
            cgeniusConfig.set("Video", "gameHeight", "480")
            cgeniusConfig.set("Video", "gameWidth", "640")
    else:
        cgeniusConfig.set("Video", "gameHeight", "200")
        cgeniusConfig.set("Video", "gameWidth", "320")
    # mouse
    if system.isOptSet("cgenius_cursor"):
        cgeniusConfig.set("Video", "ShowCursor", system.config["cgenius_cursor"])
    else:
        cgeniusConfig.set("Video", "ShowCursor", "false")


# Show mouse on screen for the Config Screen
def getMouseMode(config: Any, rom: str) -> bool:
    return True
