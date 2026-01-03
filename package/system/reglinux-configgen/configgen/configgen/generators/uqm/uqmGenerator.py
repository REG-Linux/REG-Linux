from os import makedirs

import controllers as controllersConfig

from configgen.Command import Command
from configgen.generators.Generator import Generator

UQM_BIN_PATH = "/usr/bin/urquan"


class UqmGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        directories = [
            "/userdata/saves/uqm",
            "/userdata/saves/uqm/teams",
            "/userdata/saves/uqm/save",
        ]

        for directory in directories:
            makedirs(directory, exist_ok=True)

        with open("/userdata/roms/uqm/version", "a"):  # Create file if does not exist
            pass

        command_array = [
            UQM_BIN_PATH,
            "--contentdir=/userdata/roms/uqm",
            "--configdir=/userdata/saves/uqm",
        ]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
