from generators.Generator import Generator
from Command import Command
import controllers as controllersConfig
from . import applewinConfig

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [applewinConfig.applewinBin, "--no-imgui", "--d1", rom]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generate_sdl_controller_config(playersControllers)
                    })
