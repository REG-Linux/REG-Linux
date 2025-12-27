from hashlib import md5
from os import path
from typing import Any

from configgen.settings import UnixSettings


def setSonicretroConfig(system: Any, emu: str, rom: str) -> None:
    SONICRETRO_CONFIG_PATH = rom + "/settings.ini"

    # ini file
    sonicConfig = UnixSettings(SONICRETRO_CONFIG_PATH)

    # [Dev]
    sonicConfig.ensure_section("Dev")
    if system.isOptSet("devmenu") and system.config["devmenu"] == "1":
        sonicConfig.set("Dev", "DevMenu", "true")
    else:
        sonicConfig.set("Dev", "DevMenu", "false")
    sonicConfig.set("Dev", "EngineDebugMode", "false")
    if emu == "sonic2013":
        sonicConfig.set("Dev", "StartingCategory", "255")
        sonicConfig.set("Dev", "StartingScene", "255")
        sonicConfig.set("Dev", "StartingPlayer", "255")
        sonicConfig.set("Dev", "StartingSaveFile", "255")
    else:
        sonicConfig.set("Dev", "StartingCategory", "0")
        sonicConfig.set("Dev", "StartingScene", "0")
        sonicConfig.set("Dev", "UseSteamDir", "false")
    sonicConfig.set("Dev", "FastForwardSpeed", "8")
    if system.isOptSet("hqmode") and system.config["hqmode"] == "0":
        sonicConfig.set("Dev", "UseHQModes", "false")
    else:
        sonicConfig.set("Dev", "UseHQModes", "true")
    sonicConfig.set("Dev", "DataFile", "Data.rsdk")

    # [Game]
    sonicConfig.ensure_section("Game")

    if emu == "sonic2013":
        if system.isOptSet("skipstart") and system.config["skipstart"] == "1":
            sonicConfig.set("Game", "SkipStartMenu", "true")
        else:
            sonicConfig.set("Game", "SkipStartMenu", "false")
    else:
        if system.isOptSet("spindash"):
            sonicConfig.set("Game", "OriginalControls", system.config["spindash"])
        else:
            sonicConfig.set("Game", "OriginalControls", "-1")
        sonicConfig.set("Game", "DisableTouchControls", "true")

    originsGameConfig = [
        # Sonic 1
        "5250b0e2effa4d48894106c7d5d1ad32",
        "5771433883e568715e7ac994bb22f5ed",
        # Sonic 2
        "f958285af4a09d2023b4e4f453691c4f",
        "9fe2dae0a8a2c7d8ef0bed639b3c749f",
        # Sonic CD
        "e723aab26026e4e6d4522c4356ef5a98",
    ]
    if (
        path.isfile(f"{rom}/Data/Game/GameConfig.bin")
        and system.__getMD5(f"{rom}/Data/Game/GameConfig.bin") in originsGameConfig
    ):
        sonicConfig.set("Game", "GameType", "1")

    if system.isOptSet("language"):
        sonicConfig.set("Game", "Language", system.config["language"])
    else:
        sonicConfig.set("Game", "Language", "0")

    # [Window]
    sonicConfig.ensure_section("Window")

    sonicConfig.set("Window", "FullScreen", "true")
    sonicConfig.set("Window", "Borderless", "true")
    if system.isOptSet("vsync") and system.config["vsync"] == "0":
        sonicConfig.set("Window", "VSync", "false")
    else:
        sonicConfig.set("Window", "VSync", "true")
    if system.isOptSet("scalingmode"):
        sonicConfig.set("Window", "ScalingMode", system.config["scalingmode"])
    else:
        sonicConfig.set("Window", "ScalingMode", "2")
    sonicConfig.set("Window", "WindowScale", "2")
    sonicConfig.set("Window", "ScreenWidth", "424")
    sonicConfig.set("Window", "RefreshRate", "60")
    sonicConfig.set("Window", "DimLimit", "-1")

    # [Audio]
    sonicConfig.ensure_section("Audio")

    sonicConfig.set("Audio", "BGMVolume", "1.000000")
    sonicConfig.set("Audio", "SFXVolume", "1.000000")


def getMouseMode(self: Any, config: Any, rom: str) -> bool:
    # Determine the emulator to use
    emu = "sonic2013" if (rom.lower()).endswith("son") else "soniccd"

    mouseRoms = [
        "1bd5ad366df1765c98d20b53c092a528",  # iOS version of SonicCD
    ]

    enableMouse = False
    if emu == "soniccd" and path.isfile(f"{rom}/Data.rsdk"):
        enableMouse = self.__getMD5(f"{rom}/Data.rsdk") in mouseRoms
    else:
        enableMouse = False

    return enableMouse


def __getMD5(self: Any, filename: str) -> str:
    rp = path.realpath(filename)

    # Use an instance attribute for caching instead of function attribute
    if not hasattr(self, "_md5_cache"):
        self._md5_cache = {}

    if rp in self._md5_cache:
        return self._md5_cache[rp]
    with open(rp, "rb") as f:
        md5_hash = md5(f.read()).hexdigest()
    self._md5_cache[rp] = md5_hash
    return md5_hash
