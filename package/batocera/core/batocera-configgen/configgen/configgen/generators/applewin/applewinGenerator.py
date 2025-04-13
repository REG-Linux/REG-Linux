#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
import controllersConfig
from settings.unixSettings import UnixSettings
from utils.logger import get_logger
from . import applewinConfig

eslog = get_logger(__name__)

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if not os.path.exists(applewinConfig.CONFIGDIR):
            os.makedirs(applewinConfig.CONFIGDIR)

        config = UnixSettings(applewinConfig.CONFIGFILE, separator=' ')

        rombase=os.path.basename(rom)
        romext=os.path.splitext(rombase)[1]

        config.write()
        commandArray = ["applewin" ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
