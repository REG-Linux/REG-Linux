from generators.Generator import Generator
from Command import Command
import os
import controllers as controllersConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class OpenJazzGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/openjazz/")
        except:
            eslog.error("ERROR: Game assets not installed. You can install your own or get them from the Content Downloader.")
        commandArray = ["OpenJazz", "-f", "/userdata/roms/openjazz/" + rom]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generate_sdl_controller_config(playersControllers)
                    })
