from generators.Generator import Generator
from Command import Command

class RuffleGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["ruffle", "--fullscreen", rom]
        return Command(
            array=commandArray)

    def getMouseMode(self, config, rom):
        return True
