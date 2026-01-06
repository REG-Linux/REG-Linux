from os import makedirs, path
from shutil import copy

from configgen.Command import Command
from configgen.generators.Generator import Generator

try:
    from configobj import ConfigObj
except ImportError:
    print("configobj module not found. Please install it with: pip install configobj")
    raise
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
        if not path.exists(CGENIUS_CONFIG_DIR):
            makedirs(CGENIUS_CONFIG_DIR)

        if not path.exists(CGENIUS_CONFIG_PATH):
            cgeniusConfig = ConfigObj()
            cgeniusConfig.filename = CGENIUS_CONFIG_PATH
        else:
            cgeniusConfig = ConfigObj(infile=CGENIUS_CONFIG_PATH)

        setCgeniusConfig(cgeniusConfig, system)
        setCgeniusControllers(cgeniusConfig, players_controllers)

        # Write the config file
        cgeniusConfig.write()
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
