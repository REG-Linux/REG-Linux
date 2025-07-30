from generators.Generator import Generator
from Command import Command
import os
import controllers as controllersConfig
from . import cdogsConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class CdogsGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        try:
            for assetdir in cdogsConfig.cdogsAssets:
                os.chdir(f"{cdogsConfig.cdogsRoms}/{assetdir}")
            os.chdir(cdogsConfig.cdogsRoms)
        except FileNotFoundError:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
            raise

        commandArray = [cdogsConfig.cdogsBin]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generate_sdl_controller_config(playersControllers)
                    })
