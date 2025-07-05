#!/usr/bin/env python3

from generators.Generator import Generator
import Command

class StellaGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Launch Stella
        commandArray = ["stella" , " ", rom ]

        return Command.Command(array=commandArray)
