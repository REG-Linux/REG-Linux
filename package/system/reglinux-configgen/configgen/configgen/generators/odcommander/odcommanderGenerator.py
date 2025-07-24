#!/usr/bin/env python3

from generators.Generator import Generator
import Command

class OdcommanderGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["od-commander"]

        return Command.Command(array=commandArray)
