#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import controllersConfig
from . import cdogsConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class CdogsGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        try:
            for assetdir in cdogsConfig.cdogsAssets:
                os.chdir(f"{cdogsConfig.cdogsRoms}/{cdogsConfig.cdogsAssets[assetdir]}")
            os.chdir(cdogsConfig.cdogsRoms)
        except FileNotFoundError:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
            raise

        commandArray = [cdogsConfig.cdogsBin]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
