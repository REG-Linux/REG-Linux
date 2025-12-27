from os import makedirs, path, unlink

from configgen.Command import Command
from configgen.generators.Generator import Generator

from .mednafenConfig import (
    MEDNAFEN_BIN_PATH,
    MEDNAFEN_CONFIG_DIR,
    MEDNAFEN_CONFIG_PATH,
    setMednafenConfig,
)
from .mednafenControllers import setMednafenControllers


class MednafenGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        if not path.exists(MEDNAFEN_CONFIG_DIR):
            makedirs(MEDNAFEN_CONFIG_DIR)

        # If config file already exists, delete it
        if path.exists(MEDNAFEN_CONFIG_PATH):
            unlink(MEDNAFEN_CONFIG_PATH)

        # Create the config file and fill it with basic data
        with open(MEDNAFEN_CONFIG_PATH, "w") as cfgConfig:
            # Basic settings
            setMednafenConfig(cfgConfig)
            # TODO: Controls configuration
            setMednafenControllers(cfgConfig)

        command_array = [MEDNAFEN_BIN_PATH, rom]
        return Command(array=command_array)
