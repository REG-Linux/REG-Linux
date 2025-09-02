from generators.Generator import Generator
from Command import Command
from controllers import generate_sdl_controller_config

STELLA_BIN_PATH = "/usr/bin/stella"


class StellaGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Launch Stella
        commandArray = [STELLA_BIN_PATH, " ", rom]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
