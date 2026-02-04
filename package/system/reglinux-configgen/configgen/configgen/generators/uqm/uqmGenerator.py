import pathlib

import controllers as controllersConfig

from configgen.command import Command
from configgen.generators.generator import Generator

UQM_BIN_PATH = "/usr/bin/urquan"


class UqmGenerator(Generator):
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
        directories = [
            "/userdata/saves/uqm",
            "/userdata/saves/uqm/teams",
            "/userdata/saves/uqm/save",
        ]

        for directory in directories:
            pathlib.Path(directory).mkdir(exist_ok=True, parents=True)

        with pathlib.Path("/userdata/roms/uqm/version").open(
            "a"
        ):  # Create file if does not exist
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
