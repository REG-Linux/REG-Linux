from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path
from shutil import copytree
from configgen.controllers import generate_sdl_controller_config
from .ioquake3Config import (
    setIoquake3Config,
    IOQUAKE3_BIN_DIR,
    IOQUAKE3_ROMS_DIR,
    IOQUAKE3_BIN_PATH,
)


class IOQuake3Generator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        setIoquake3Config(system, rom, playersControllers, gameResolution)

        # ioquake3 looks for folder either in config or from where it's launched
        destination_file = path.join(IOQUAKE3_ROMS_DIR, "/ioquake3")
        source_file = path.join(IOQUAKE3_BIN_DIR, "/ioquake3")

        # therefore copy latest ioquake3 file to rom directory
        if not path.isfile(destination_file) or path.getmtime(
            source_file
        ) > path.getmtime(destination_file):
            copytree(IOQUAKE3_BIN_DIR, IOQUAKE3_ROMS_DIR, dirs_exist_ok=True)

        commandArray = [IOQUAKE3_BIN_PATH]

        # get the game / mod to launch
        with open(rom, "r") as file:
            command_line = file.readline().strip()
            command_line_words = command_line.split()

        commandArray.extend(command_line_words)

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if gameResolution["width"] / float(gameResolution["height"]) > (
            (16.0 / 9.0) - 0.1
        ):
            return 16 / 9
        return 4 / 3
