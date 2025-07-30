from generators.Generator import Generator
from Command import Command
from pathlib import Path
from . import dhewm3Config

from utils.logger import get_logger
eslog = get_logger(__name__)

class Dhewm3Generator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Read the path within the .d3 rom file
        with open(rom, "r") as file:
            directory = file.readline().strip().split("/")[0]
            eslog.debug(f"Using directory: {directory}")

        # Run command
        commandArray: list[str | Path] = [
            dhewm3Config.dhewm3Bin, "+set", "fs_basepath", str(dhewm3Config.dhewm3RomDir)
        ]

        if directory != "base":
            commandArray.extend([
                "+set", "fs_game", str(directory)
            ])

        return Command(array=commandArray)
