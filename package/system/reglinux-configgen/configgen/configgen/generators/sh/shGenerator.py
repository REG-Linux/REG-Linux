#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import glob

class ShGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # in case of squashfs, the root directory is passed
        shInDir = glob.glob(rom + "/run.sh")
        if len(shInDir) == 1:
            shrom = shInDir[0]
        else:
            shrom = rom

        commandArray = ["/bin/bash", shrom]

        return Command.Command(array=commandArray)

    def getMouseMode(self, config, rom):
        return True
