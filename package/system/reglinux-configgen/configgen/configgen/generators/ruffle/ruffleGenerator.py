from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config

RUFFLE_BIN_PATH = "/usr/bin/ruffle"


class RuffleGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = [RUFFLE_BIN_PATH, "--fullscreen", rom]
        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    def getMouseMode(self, config, rom):
        return True
