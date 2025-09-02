from generators.Generator import Generator
from Command import Command
from controllers import generate_sdl_controller_config

LIGHTSPARK_BIN_PATH = "/usr/bin/lightspark"


class LightsparkGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = [LIGHTSPARK_BIN_PATH, "-s", "local-with-networking", rom]
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
