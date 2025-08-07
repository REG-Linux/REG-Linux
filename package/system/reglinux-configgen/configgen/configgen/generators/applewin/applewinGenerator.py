from generators.Generator import Generator
from Command import Command
from controllers import generate_sdl_controller_config
from .applewinConfig import APPLEWIN_BIN_PATH

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [APPLEWIN_BIN_PATH, "--no-imgui", "--d1", rom]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                    })
