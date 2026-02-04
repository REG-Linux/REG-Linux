from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator

SOLARUS_BIN_PATH = "/usr/bin/solarus-run"


class SolarusGenerator(Generator):
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
        # basis
        command_array = [
            SOLARUS_BIN_PATH,
            "-fullscreen=yes",
            "-cursor-visible=no",
            "-lua-console=no",
        ]

        # rom
        command_array.append(rom)

        return Command(
            array=command_array,
            env={
                "SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS": "0",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
