from generators.Generator import Generator
from Command import Command
from os import path
from controllers import generate_sdl_controller_config

SHADPS4_BIN_PATH = "/usr/bin/shadps4/shadps4"


class Shadps4Generator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = [SHADPS4_BIN_PATH, path.dirname(rom) + "/eboot.bin"]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
