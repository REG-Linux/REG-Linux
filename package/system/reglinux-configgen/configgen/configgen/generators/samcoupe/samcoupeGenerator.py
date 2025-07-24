#!/usr/bin/env python3

from generators.Generator import Generator
import Command


class SamcoupeGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["simcoupe", "autoboot", "-disk1", rom]
        return Command.Command(array=commandArray)
