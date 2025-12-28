from pathlib import Path
from typing import Any

from configgen.systemFiles import CHEATS, CONF, SAVES

MELONDS_CONFIG_DIR = CONF / "melonDS"
MELONDS_CONFIG_PATH = MELONDS_CONFIG_DIR / "melonDS.ini"
MELONDS_SAVES_DIR = SAVES / "melonds"
MELONDS_CHEATS_DIR = CHEATS / "melonDS"
MELONDS_BIN_PATH = Path("/usr/bin/melonDS")


def setMelonDSConfig(
    melondsConfig: Any, system: Any, gameResolution: dict[str, int]
) -> None:
    if gameResolution["width"] < gameResolution["height"]:
        width, height = gameResolution["height"], gameResolution["width"]
    else:
        width, height = gameResolution["width"], gameResolution["height"]

    # [Set config defaults]
    config_dict = {
        "WindowWidth": width,
        "WindowHeight": height,
        "WindowMax": 1,
        # Hide mouse after 5 seconds
        "MouseHide": 1,
        "MouseHideSeconds": 5,
        # Set bios locations
        "ExternalBIOSEnable": 1,
        "BIOS9Path": str(Path("/userdata/bios/bios9.bin")),
        "BIOS7Path": str(Path("/userdata/bios/bios7.bin")),
        "FirmwarePath": str(Path("/userdata/bios/firmware.bin")),
        "DSiBIOS9Path": str(Path("/userdata/bios/dsi_bios9.bin")),
        "DSiBIOS7Path": str(Path("/userdata/bios/dsi_bios7.bin")),
        "DSiFirmwarePath": str(Path("/userdata/bios/dsi_firmware.bin")),
        "DSiNANDPath": str(Path("/userdata/bios/dsi_nand.bin")),
        # Set save locations
        "DLDIFolderPath": str(Path("/userdata/saves/melonds")),
        "DSiSDFolderPath": str(Path("/userdata/saves/melonds")),
        "MicWavPath": str(Path("/userdata/saves/melonds")),
        "SaveFilePath": str(Path("/userdata/saves/melonds")),
        "SavestatePath": str(Path("/userdata/saves/melonds")),
        # Cheater!
        "CheatFilePath": str(Path("/userdata/cheats/melonDS")),
        # Roms
        "LastROMFolder": str(Path("/userdata/roms/nds")),
        # Audio
        "AudioInterp": 1,
        "AudioBitrate": 2,
        "AudioVolume": 256,
        # For Software Rendering
        "Threaded3D": 1,
    }

    # Write all default config lines
    for key, value in config_dict.items():
        melondsConfig.save(key, value)

    # [User selected options]
    # MelonDS only has OpenGL or Software - use OpenGL if not selected
    if system.isOptSet("melonds_renderer"):
        melondsConfig.save("3DRenderer", system.config["melonds_renderer"])
    else:
        melondsConfig.save("3DRenderer", 1)

    if system.isOptSet("melonds_framerate"):
        melondsConfig.save("LimitFPS", system.config["melonds_framerate"])
    else:
        melondsConfig.save("LimitFPS", 1)

    if system.isOptSet("melonds_resolution"):
        melondsConfig.save("GL_ScaleFactor", system.config["melonds_resolution"])
    else:
        melondsConfig.save("GL_ScaleFactor", 1)

    if system.isOptSet("melonds_polygons"):
        melondsConfig.save("GL_BetterPolygons", system.config["melonds_polygons"])
    else:
        melondsConfig.save("GL_BetterPolygons", 0)

    if system.isOptSet("melonds_rotation"):
        melondsConfig.save("ScreenRotation", system.config["melonds_rotation"])
    else:
        melondsConfig.save("ScreenRotation", 0)

    if system.isOptSet("melonds_screenswap"):
        melondsConfig.save("ScreenSwap", system.config["melonds_screenswap"])
    else:
        melondsConfig.save("ScreenSwap", 0)

    if system.isOptSet("melonds_layout"):
        melondsConfig.save("ScreenLayout", system.config["melonds_layout"])
    else:
        melondsConfig.save("ScreenLayout", 0)

    if system.isOptSet("melonds_screensizing"):
        melondsConfig.save("ScreenSizing", system.config["melonds_screensizing"])
    else:
        melondsConfig.save("ScreenSizing", 0)

    if system.isOptSet("melonds_scaling"):
        melondsConfig.save("IntegerScaling", system.config["melonds_scaling"])
    else:
        melondsConfig.save("IntegerScaling", 0)

    # Cheater!
    if system.isOptSet("melonds_cheats"):
        melondsConfig.save("EnableCheats", system.config["melonds_cheats"])
    else:
        melondsConfig.save("EnableCheats", 0)
    if system.isOptSet("melonds_osd"):
        melondsConfig.save("ShowOSD", system.config["melonds_osd"])
    else:
        melondsConfig.save("ShowOSD", 1)
    if system.isOptSet("melonds_console"):
        melondsConfig.save("ConsoleType", system.config["melonds_console"])
    else:
        melondsConfig.save("ConsoleType", 0)
