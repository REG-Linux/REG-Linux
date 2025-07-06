#!/usr/bin/env python3

from generators.Generator import Generator
import Command
from . import bigpemuConfig

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        bigpemuConfig.readWriteFile(system, gameResolution, playersControllers)

        commandArray = [bigpemuConfig.bigpemuBin, rom]
        return Command.Command(array=commandArray)
