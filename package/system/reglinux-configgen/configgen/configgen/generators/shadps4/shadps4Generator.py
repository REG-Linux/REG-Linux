from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path
from configgen.controllers import generate_sdl_controller_config

SHADPS4_BIN_PATH = "/usr/bin/shadps4/shadps4"


class Shadps4Generator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        command_array = [SHADPS4_BIN_PATH, path.dirname(rom) + "/eboot.bin"]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
