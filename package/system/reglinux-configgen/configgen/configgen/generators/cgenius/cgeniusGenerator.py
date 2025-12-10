from configgen.generators.Generator import Generator
from os import path, makedirs
from configgen.Command import Command
from shutil import copy
from configobj import ConfigObj
from .cgeniusControllers import setCgeniusControllers
from .cgeniusConfig import (
    CGENIUS_CONFIG_DIR,
    CGENIUS_CONFIG_PATH,
    CGENIUS_ROMS_DIR,
    CGENIUS_BIN_PATH,
    setCgeniusConfig,
)


class CGeniusGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
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
        setCgeniusControllers(cgeniusConfig, playersControllers)

        # Write the config file
        cgeniusConfig.write()
        # need to copy to roms folder too
        copy(CGENIUS_CONFIG_PATH, CGENIUS_ROMS_DIR)

        # now setup to run the rom
        commandArray = [CGENIUS_BIN_PATH]

        # get rom path
        rom_path = path.dirname(rom)
        rom_path = rom_path.replace(CGENIUS_ROMS_DIR, "")
        dir_string = 'dir="' + rom_path + '"'
        commandArray.append(dir_string)

        return Command(array=commandArray)
