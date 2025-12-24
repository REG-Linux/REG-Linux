from os import path
from shutil import copytree

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator

from .ioquake3Config import (
    IOQUAKE3_BIN_DIR,
    IOQUAKE3_BIN_PATH,
    IOQUAKE3_ROMS_DIR,
    setIoquake3Config,
)


class IOQuake3Generator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        setIoquake3Config(system, rom, players_controllers, game_resolution)

        # ioquake3 looks for folder either in config or from where it's launched
        destination_file = path.join(IOQUAKE3_ROMS_DIR, "/ioquake3")
        source_file = path.join(IOQUAKE3_BIN_DIR, "/ioquake3")

        # therefore copy latest ioquake3 file to rom directory
        if not path.isfile(destination_file) or path.getmtime(
            source_file
        ) > path.getmtime(destination_file):
            copytree(IOQUAKE3_BIN_DIR, IOQUAKE3_ROMS_DIR, dirs_exist_ok=True)

        command_array = [IOQUAKE3_BIN_PATH]

        # get the game / mod to launch
        with open(rom) as file:
            command_line = file.readline().strip()
            command_line_words = command_line.split()

        command_array.extend(command_line_words)

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    def get_in_game_ratio(self, config, game_resolution, rom):
        if game_resolution["width"] / float(game_resolution["height"]) > (
            (16.0 / 9.0) - 0.1
        ):
            return 16 / 9
        return 4 / 3
