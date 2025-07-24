#!/usr/bin/env python3

from generators.Generator import Generator
import Command
from . import cannonballConfig

class CannonballGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # cannonball config file
        cannonballConfig.setCannonballConfig(system)

        # command line
        commandArray = [cannonballConfig.cannonballBin]

        return Command.Command(array=commandArray)
