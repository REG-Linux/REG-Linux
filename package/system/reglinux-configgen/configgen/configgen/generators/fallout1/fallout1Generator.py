from configgen.generators.Generator import Generator
from configgen.Command import Command
from configparser import ConfigParser
from os import path, makedirs, chdir
from shutil import copy
from .fallout1Config import (
    setFalloutConfig,
    setFalloutIniConfig,
    FALLOUT_CONFIG_DIR,
    FALLOUT_EXE_SOURCE_PATH,
    FALLOUT_BIN_PATH,
    FALLOUT_CONFIG_PATH,
    FALLOUT_CONFIG_INI,
    FALLOUT_ROMS_DIR,
    FALLOUT_CONFIG_SOURCE_PATH,
    FALLOUT_CONFIG_INI_SOURCE_PATH,
)
from configgen.controllers import generate_sdl_controller_config


class Fallout1Generator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
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

        setFalloutIniConfig(falloutIniConfig, gameResolution)

        with open(FALLOUT_CONFIG_INI, "w") as configfile:
            falloutIniConfig.write(configfile)

        # IMPORTANT: Move dir before executing
        chdir(FALLOUT_ROMS_DIR)

        ## Setup the command
        commandArray = [FALLOUT_BIN_PATH]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
