from generators.Generator import Generator
from Command import Command
import os
import controllers as controllersConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class TyrianGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/tyrian/data")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["opentyrian"]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generate_sdl_controller_config(playersControllers)
                    })

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
