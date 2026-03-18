from configparser import ConfigParser
from pathlib import Path
from typing import Any

from configgen.core import Command
from configgen.generators.generator import Generator

from .mupen64plusConfig import (
    MUPEN64PLUS_BIN_PATH,
    MUPEN64PLUS_CONFIG_DIR,
    MUPEN64PLUS_CONFIG_PATH,
    setMupen64plusConfig,
)


class Mupen64plusGenerator(Generator):
    def generate(
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    ):
        # Read the configuration file
        iniConfig = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = lambda optionstr: str(optionstr)
        config_path = Path(MUPEN64PLUS_CONFIG_PATH)
        if config_path.exists():
            iniConfig.read(MUPEN64PLUS_CONFIG_PATH)
        else:
            config_dir = config_path.parent
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
            iniConfig.read(MUPEN64PLUS_CONFIG_PATH)

        setMupen64plusConfig(iniConfig, system, game_resolution)

        # Save the ini file
        config_dir = config_path.parent
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
        with Path(MUPEN64PLUS_CONFIG_PATH).open("w") as configfile:
            iniConfig.write(configfile)

        # Command
        command_array = [
            str(MUPEN64PLUS_BIN_PATH),
            "--plugindir",
            "/usr/lib/mupen64plus/",
            "--corelib",
            "libmupen64plus.so.2.0.0",
            "--gfx",
            f"mupen64plus-video-{system.config['core']}.so",
            "--audio",
            "mupen64plus-audio-sdl.so",
            "--input",
            "mupen64plus-input-sdl.so",
            "--rsp",
            "mupen64plus-rsp-hle.so",
            "--configdir",
            MUPEN64PLUS_CONFIG_DIR,
            "--datadir",
            MUPEN64PLUS_CONFIG_DIR,
        ]

        # state_slot option
        if system.isOptSet("state_filename"):
            command_array.extend(["--savestate", system.config["state_filename"]])

        command_array.append(rom)

        return Command(array=command_array)

    def get_in_game_ratio(self, config: Any) -> float:
        if (
            "mupen64plus_ratio" in config and config["mupen64plus_ratio"] == "16/9"
        ) or (
            "mupen64plus_ratio" not in config
            and "ratio" in config
            and config["ratio"] == "16/9"
        ):
            return 16 / 9
        return 4 / 3
