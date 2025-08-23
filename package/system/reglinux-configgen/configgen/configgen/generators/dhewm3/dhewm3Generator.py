from generators.Generator import Generator
from Command import Command
from pathlib import Path
from systemFiles import CONF, ROMS

DHEWM3_BIN_PATH = '/usr/bin/dhewm3'
DHEWM3_CONFIG_DIR = CONF + '/dhewm3'
DHEWM3_ROMS_DIR = ROMS + '/doom3'

class Dhewm3Generator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Read the path within the .d3 rom file
        with open(rom, "r") as file:
            directory = file.readline().strip().split("/")[0]

        # Run command
        commandArray: list[str | Path] = [
            DHEWM3_BIN_PATH, "+set", "fs_basepath", str(DHEWM3_ROMS_DIR)
        ]

        if directory != "base":
            commandArray.extend([
                "+set", "fs_game", str(directory)
            ])

        return Command(array=commandArray)
