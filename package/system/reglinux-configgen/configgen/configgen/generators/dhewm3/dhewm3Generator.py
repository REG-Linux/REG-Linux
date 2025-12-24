from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF, ROMS

DHEWM3_BIN_PATH = "/usr/bin/dhewm3"
DHEWM3_CONFIG_DIR = CONF + "/dhewm3"
DHEWM3_ROMS_DIR = ROMS + "/doom3"


class Dhewm3Generator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Read the path within the .d3 rom file
        with open(rom) as file:
            directory = file.readline().strip().split("/")[0]

        # Run command
        command_array = [
            DHEWM3_BIN_PATH,
            "+set",
            "fs_basepath",
            str(DHEWM3_ROMS_DIR),
        ]

        if directory != "base":
            command_array.extend(["+set", "fs_game", str(directory)])

        # Convert any Path objects to strings to ensure all elements are strings
        command_array = [str(item) for item in command_array]

        return Command(array=command_array)
