from configparser import ConfigParser
from os import chdir, makedirs, path
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
        if not path.exists(FALLOUT_CONFIG_DIR):
            makedirs(FALLOUT_CONFIG_DIR)

        # Copy latest binary to the rom directory
        if not path.exists(FALLOUT_EXE_SOURCE_PATH):
            copy(FALLOUT_BIN_PATH, FALLOUT_EXE_SOURCE_PATH)
        else:
            source_version = path.getmtime(FALLOUT_BIN_PATH)
            destination_version = path.getmtime(FALLOUT_EXE_SOURCE_PATH)
            if source_version > destination_version:
                copy(FALLOUT_BIN_PATH, FALLOUT_EXE_SOURCE_PATH)

        # Copy cfg file to the config directory
        if not path.exists(FALLOUT_CONFIG_PATH):
            if path.exists(FALLOUT_CONFIG_SOURCE_PATH):
                copy(FALLOUT_CONFIG_SOURCE_PATH, FALLOUT_CONFIG_PATH)

        # Now copy the ini file to the config directory
        if not path.exists(FALLOUT_CONFIG_INI):
            if path.exists(FALLOUT_CONFIG_INI_SOURCE_PATH):
                copy(FALLOUT_CONFIG_INI_SOURCE_PATH, FALLOUT_CONFIG_INI)

        # CFG Configuration
        falloutConfig = ConfigParser()
        falloutConfig.optionxform = lambda optionstr: str(optionstr)
        if path.exists(FALLOUT_CONFIG_PATH):
            falloutConfig.read(FALLOUT_CONFIG_PATH)

        setFalloutConfig(falloutConfig, system)

        with open(FALLOUT_CONFIG_PATH, "w") as configfile:
            falloutConfig.write(configfile)

        ## INI Configuration
        falloutIniConfig = ConfigParser()
        falloutIniConfig.optionxform = lambda optionstr: str(optionstr)
        if path.exists(FALLOUT_CONFIG_INI):
            falloutIniConfig.read(FALLOUT_CONFIG_INI)

        setFalloutIniConfig(falloutIniConfig, game_resolution)

        with open(FALLOUT_CONFIG_INI, "w") as configfile:
            falloutIniConfig.write(configfile)

        # IMPORTANT: Move dir before executing
        chdir(FALLOUT_ROMS_DIR)

        ## Setup the command
        command_array = [FALLOUT_BIN_PATH]

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
