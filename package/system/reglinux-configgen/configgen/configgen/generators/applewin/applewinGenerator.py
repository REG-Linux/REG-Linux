#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import controllersConfig
from settings.unixSettings import UnixSettings
from . import applewinConfig

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if not os.path.exists(applewinConfig.CONFIGDIR):
            os.makedirs(applewinConfig.CONFIGDIR)

        config = UnixSettings(applewinConfig.CONFIGFILE, separator=' ')

        rombase=os.path.basename(rom)
        romext=os.path.splitext(rombase)[1]

        config.write()
        commandArray = [applewinConfig.applewinBin]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
