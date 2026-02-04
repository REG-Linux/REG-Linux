import pathlib
from configparser import ConfigParser
from os import path
from shutil import copy

from configgen.command import Command
from configgen.generators.generator import Generator

from .cgeniusConfig import (
    CGENIUS_BIN_PATH,
    CGENIUS_CONFIG_DIR,
    CGENIUS_CONFIG_PATH,
    CGENIUS_ROMS_DIR,
    setCgeniusConfig,
)
from .cgeniusControllers import setCgeniusControllers


class CGeniusGenerator(Generator):
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
        # Create the config directory if it doesn't exist
        if not pathlib.Path(CGENIUS_CONFIG_DIR).exists():
            pathlib.Path(CGENIUS_CONFIG_DIR).mkdir(parents=True)

        cgeniusConfig = ConfigParser()

        if pathlib.Path(CGENIUS_CONFIG_PATH).exists():
            cgeniusConfig.read(CGENIUS_CONFIG_PATH)

        setCgeniusConfig(cgeniusConfig, system)
        setCgeniusControllers(cgeniusConfig, players_controllers)

        # Write the config file
        with pathlib.Path(CGENIUS_CONFIG_PATH).open("w") as configfile:
            cgeniusConfig.write(configfile)
        # need to copy to roms folder too
        copy(CGENIUS_CONFIG_PATH, CGENIUS_ROMS_DIR)

        # now setup to run the rom
        command_array = [CGENIUS_BIN_PATH]

        # get rom path
        rom_path = path.dirname(rom)
        rom_path = rom_path.replace(CGENIUS_ROMS_DIR, "")
        dir_string = 'dir="' + rom_path + '"'
        command_array.append(dir_string)

        return Command(array=command_array)
