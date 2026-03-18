from pathlib import Path
from typing import Any

from configgen.config.paths import CHEATS, CONF, SAVES

MELONDS_CONFIG_DIR = CONF / "melonDS"
MELONDS_CONFIG_PATH = MELONDS_CONFIG_DIR / "melonDS.toml"
MELONDS_SAVES_DIR = SAVES / "melonds"
MELONDS_CHEATS_DIR = CHEATS / "melonDS"
MELONDS_BIN_PATH = Path("/usr/bin/melonDS")


def setMelonDSConfig(
    melondsConfig: Any,
    system: Any,
    gameResolution: dict[str, int],
) -> None:
    if gameResolution["width"] < gameResolution["height"]:
        width, height = gameResolution["height"], gameResolution["width"]
    else:
        width, height = gameResolution["width"], gameResolution["height"]

    # [Set config defaults]
    # Simple values at root level
    melondsConfig["WindowWidth"] = width
    melondsConfig["WindowHeight"] = height
    melondsConfig["WindowMax"] = True
    melondsConfig["MouseHide"] = True
    melondsConfig["MouseHideSeconds"] = 5
    melondsConfig["LastROMFolder"] = str(Path("/userdata/roms/nds"))
    melondsConfig["LastBIOSFolder"] = str(Path("/userdata/bios"))
    melondsConfig["SavestatePath"] = str(Path("/userdata/saves/melonds"))
    melondsConfig["SaveFilePath"] = str(Path("/userdata/saves/melonds"))
    melondsConfig["CheatFilePath"] = str(Path("/userdata/cheats/melonDS"))
    melondsConfig["DLDIFolderPath"] = str(Path("/userdata/saves/melonds"))
    melondsConfig["DSiSDFolderPath"] = str(Path("/userdata/saves/melonds"))
    melondsConfig["MicWavPath"] = str(Path("/userdata/saves/melonds"))

    # [DS] - BIOS paths for original DS
    if "DS" not in melondsConfig:
        melondsConfig["DS"] = {}
    melondsConfig["DS"]["BIOS9Path"] = str(Path("/userdata/bios/bios9.bin"))
    melondsConfig["DS"]["BIOS7Path"] = str(Path("/userdata/bios/bios7.bin"))
    melondsConfig["DS"]["FirmwarePath"] = str(Path("/userdata/bios/firmware.bin"))

    # [DSi] - BIOS paths for DSi
    if "DSi" not in melondsConfig:
        melondsConfig["DSi"] = {}
    melondsConfig["DSi"]["BIOS9Path"] = str(Path("/userdata/bios/dsi_bios9.bin"))
    melondsConfig["DSi"]["BIOS7Path"] = str(Path("/userdata/bios/dsi_bios7.bin"))
    melondsConfig["DSi"]["FirmwarePath"] = str(Path("/userdata/bios/dsi_firmware.bin"))
    melondsConfig["DSi"]["NANDPath"] = str(Path("/userdata/bios/dsi_nand.bin"))

    # [DSi.SD] - DSi SD card
    if "DSi" not in melondsConfig:
        melondsConfig["DSi"] = {}
    if "SD" not in melondsConfig["DSi"]:
        melondsConfig["DSi"]["SD"] = {}
    melondsConfig["DSi"]["SD"]["FolderPath"] = str(Path("/userdata/saves/melonds"))

    # [DLDI] - DLDI settings
    if "DLDI" not in melondsConfig:
        melondsConfig["DLDI"] = {}
    melondsConfig["DLDI"]["FolderPath"] = str(Path("/userdata/saves/melonds"))
    melondsConfig["DLDI"]["Enable"] = True

    # [Emu] - Emulator settings
    if "Emu" not in melondsConfig:
        melondsConfig["Emu"] = {}
    melondsConfig["Emu"]["ExternalBIOSEnable"] = True
    melondsConfig["Emu"]["DirectBoot"] = True
    melondsConfig["Emu"]["ConsoleType"] = 0  # 0 = DS, 1 = DSi

    # [3D] - 3D rendering settings
    if "3D" not in melondsConfig:
        melondsConfig["3D"] = {}
    melondsConfig["3D"]["Renderer"] = 1  # 0 = Software, 1 = OpenGL
    melondsConfig["3D"]["LimitFPS"] = True

    # [3D.GL] - OpenGL settings
    if "GL" not in melondsConfig["3D"]:
        melondsConfig["3D"]["GL"] = {}
    melondsConfig["3D"]["GL"]["ScaleFactor"] = 1
    melondsConfig["3D"]["GL"]["BetterPolygons"] = False

    # [Screen] - Screen settings
    if "Screen" not in melondsConfig:
        melondsConfig["Screen"] = {}
    melondsConfig["Screen"]["VSync"] = False
    melondsConfig["Screen"]["UseGL"] = True

    # [Instance0] - Instance-specific settings
    if "Instance0" not in melondsConfig:
        melondsConfig["Instance0"] = {}

    # [Instance0.Window0] - Main window settings
    if "Window0" not in melondsConfig["Instance0"]:
        melondsConfig["Instance0"]["Window0"] = {}
    melondsConfig["Instance0"]["Window0"]["ScreenRotation"] = 0
    melondsConfig["Instance0"]["Window0"]["ScreenSwap"] = False
    melondsConfig["Instance0"]["Window0"]["ScreenLayout"] = 0
    melondsConfig["Instance0"]["Window0"]["ScreenSizing"] = 0
    melondsConfig["Instance0"]["Window0"]["IntegerScaling"] = False
    melondsConfig["Instance0"]["Window0"]["ShowOSD"] = True

    # [Instance0.Window1] - Second window settings (dual screen)
    if "Window1" not in melondsConfig["Instance0"]:
        melondsConfig["Instance0"]["Window1"] = {}
    melondsConfig["Instance0"]["Window1"]["Enabled"] = False
    melondsConfig["Instance0"]["Window1"]["ScreenRotation"] = 0
    melondsConfig["Instance0"]["Window1"]["ScreenSwap"] = False
    melondsConfig["Instance0"]["Window1"]["ScreenLayout"] = 0
    melondsConfig["Instance0"]["Window1"]["ScreenSizing"] = 5
    melondsConfig["Instance0"]["Window1"]["IntegerScaling"] = False

    # NOTE: Instance0.Joystick is handled by setMelondsControllers

    # [User selected options]
    # Renderer
    if system.isOptSet("melonds_renderer"):
        renderer = system.config["melonds_renderer"]
        melondsConfig["3D"]["Renderer"] = renderer
        melondsConfig["Screen"]["UseGL"] = renderer != 0
    else:
        melondsConfig["3D"]["Renderer"] = 1
        melondsConfig["Screen"]["UseGL"] = True

    # Framerate limit
    if system.isOptSet("melonds_framerate"):
        melondsConfig["3D"]["LimitFPS"] = system.config["melonds_framerate"]
    else:
        melondsConfig["3D"]["LimitFPS"] = True

    # Resolution scale
    if system.isOptSet("melonds_resolution"):
        melondsConfig["3D"]["GL"]["ScaleFactor"] = system.config["melonds_resolution"]
    else:
        melondsConfig["3D"]["GL"]["ScaleFactor"] = 1

    # Better polygons
    if system.isOptSet("melonds_polygons"):
        melondsConfig["3D"]["GL"]["BetterPolygons"] = system.config["melonds_polygons"]
    else:
        melondsConfig["3D"]["GL"]["BetterPolygons"] = False

    # Screen rotation
    if system.isOptSet("melonds_rotation"):
        melondsConfig["Instance0"]["Window0"]["ScreenRotation"] = system.config[
            "melonds_rotation"
        ]
    else:
        melondsConfig["Instance0"]["Window0"]["ScreenRotation"] = 0

    # Screen swap
    if system.isOptSet("melonds_screenswap"):
        melondsConfig["Instance0"]["Window0"]["ScreenSwap"] = system.config[
            "melonds_screenswap"
        ]
    else:
        melondsConfig["Instance0"]["Window0"]["ScreenSwap"] = False

    # Screen layout
    if system.isOptSet("melonds_layout"):
        melondsConfig["Instance0"]["Window0"]["ScreenLayout"] = system.config[
            "melonds_layout"
        ]
    else:
        melondsConfig["Instance0"]["Window0"]["ScreenLayout"] = 0

    # Screen sizing
    if system.isOptSet("melonds_screensizing"):
        melondsConfig["Instance0"]["Window0"]["ScreenSizing"] = system.config[
            "melonds_screensizing"
        ]
    else:
        melondsConfig["Instance0"]["Window0"]["ScreenSizing"] = 0

    # Integer scaling
    if system.isOptSet("melonds_scaling"):
        melondsConfig["Instance0"]["Window0"]["IntegerScaling"] = system.config[
            "melonds_scaling"
        ]
    else:
        melondsConfig["Instance0"]["Window0"]["IntegerScaling"] = False

    # Enable cheats
    if system.isOptSet("melonds_cheats"):
        melondsConfig["Instance0"]["EnableCheats"] = system.config["melonds_cheats"]
    else:
        melondsConfig["Instance0"]["EnableCheats"] = False

    # Show OSD
    if system.isOptSet("melonds_osd"):
        melondsConfig["Instance0"]["Window0"]["ShowOSD"] = system.config["melonds_osd"]
    else:
        melondsConfig["Instance0"]["Window0"]["ShowOSD"] = True

    # Console type
    if system.isOptSet("melonds_console"):
        melondsConfig["Emu"]["ConsoleType"] = system.config["melonds_console"]
    else:
        melondsConfig["Emu"]["ConsoleType"] = 0
