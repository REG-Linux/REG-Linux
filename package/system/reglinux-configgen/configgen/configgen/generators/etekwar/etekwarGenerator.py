#!/usr/bin/env python3

from generators.Generator import Generator
import Command

class EtekwarGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["etekwar", rom]

        return Command.Command(array=commandArray)
