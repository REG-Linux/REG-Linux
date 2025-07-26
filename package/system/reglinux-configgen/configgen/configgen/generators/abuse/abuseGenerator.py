#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import controllers as controllersConfig
from . import abuseConfig

class AbuseGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = [abuseConfig.abuseBin, "-datadir", abuseConfig.abuseDataDir]

        return Command.Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
                    })
