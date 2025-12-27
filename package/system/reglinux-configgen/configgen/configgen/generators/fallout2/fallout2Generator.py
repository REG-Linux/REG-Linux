from configparser import ConfigParser
from os import chdir
from pathlib import Path
from shutil import copy
from typing import Any

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator

from .fallout2Config import (
    FALLOUT_BIN_PATH,
    FALLOUT_CONFIG_DIR,
    FALLOUT_CONFIG_INI,
    FALLOUT_CONFIG_INI_SOURCE_PATH,
    FALLOUT_CONFIG_PATH,
    FALLOUT_CONFIG_SOURCE_PATH,
    FALLOUT_EXE_SOURCE_PATH,
    FALLOUT_ROMS_DIR,
    setFalloutConfig,
    setFalloutIniConfig,
)


class Fallout2Generator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Check if the directories exist, if not create them
        config_dir_path = Path(FALLOUT_CONFIG_DIR)
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)

        # Copy latest binary to the rom directory
        exe_source_path = Path(FALLOUT_EXE_SOURCE_PATH)
        if not exe_source_path.exists():
            copy(FALLOUT_BIN_PATH, FALLOUT_EXE_SOURCE_PATH)
        else:
            source_version = Path(FALLOUT_BIN_PATH).stat().st_mtime
            destination_version = exe_source_path.stat().st_mtime
            if source_version > destination_version:
                copy(FALLOUT_BIN_PATH, FALLOUT_EXE_SOURCE_PATH)

        # Copy cfg file to the config directory
        config_path = Path(FALLOUT_CONFIG_PATH)
        config_source_path = Path(FALLOUT_CONFIG_SOURCE_PATH)
        if not config_path.exists() and config_source_path.exists():
            copy(FALLOUT_CONFIG_SOURCE_PATH, FALLOUT_CONFIG_PATH)

        # Now copy the ini file to the config directory
        config_ini_path = Path(FALLOUT_CONFIG_INI)
        config_ini_source_path = Path(FALLOUT_CONFIG_INI_SOURCE_PATH)
        if not config_ini_path.exists() and config_ini_source_path.exists():
            copy(FALLOUT_CONFIG_INI_SOURCE_PATH, FALLOUT_CONFIG_INI)

        # CFG Configuration
        falloutConfig = ConfigParser()
        falloutConfig.optionxform = lambda optionstr: str(optionstr)
        if config_path.exists():
            falloutConfig.read(FALLOUT_CONFIG_PATH)

        setFalloutConfig(falloutConfig, system)

        with open(FALLOUT_CONFIG_PATH, "w") as configfile:
            falloutConfig.write(configfile)

        ## INI Configuration
        falloutIniConfig = ConfigParser()
        falloutIniConfig.optionxform = lambda optionstr: str(optionstr)
        config_ini_path = Path(FALLOUT_CONFIG_INI)
        if config_ini_path.exists():
            falloutIniConfig.read(FALLOUT_CONFIG_INI)

        setFalloutIniConfig(falloutIniConfig, game_resolution)

        with open(FALLOUT_CONFIG_INI, "w") as configfile:
            falloutIniConfig.write(configfile)

        # IMPORTANT: Move dir before executing
        chdir(FALLOUT_ROMS_DIR)

        ## Setup the command
        command_array = [str(FALLOUT_BIN_PATH)]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config: Any, rom: str) -> bool:
        return True

    def get_in_game_ratio(
        self, config: Any, game_resolution: dict[str, int], rom: str
    ) -> float:
        return 16 / 9
