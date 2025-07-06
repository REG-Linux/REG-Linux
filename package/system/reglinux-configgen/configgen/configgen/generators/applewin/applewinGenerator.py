#!/usr/bin/env python3

from generators.Generator import Generator
import Command
from . import applewinConfig

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [applewinConfig.applewinBin, "--no-imgui", "--d1", rom]
        return Command.Command(array=commandArray)
