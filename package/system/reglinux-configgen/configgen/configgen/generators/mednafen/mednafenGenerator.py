from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs, unlink
from .mednafenControllers import setMednafenControllers
from .mednafenConfig import (
    setMednafenConfig,
    MEDNAFEN_CONFIG_DIR,
    MEDNAFEN_CONFIG_PATH,
    MEDNAFEN_BIN_PATH,
)


class MednafenGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        if not path.exists(MEDNAFEN_CONFIG_DIR):
            makedirs(MEDNAFEN_CONFIG_DIR)

        # If config file already exists, delete it
        if path.exists(MEDNAFEN_CONFIG_PATH):
            unlink(MEDNAFEN_CONFIG_PATH)

        # Create the config file and fill it with basic data
        cfgConfig = open(MEDNAFEN_CONFIG_PATH, "w")

        # Basic settings
        setMednafenConfig(cfgConfig)
        # TODO: Controls configuration
        setMednafenControllers(cfgConfig)

        # Close config file as we are done
        cfgConfig.close()

        commandArray = [MEDNAFEN_BIN_PATH, rom]
        return Command(array=commandArray)
