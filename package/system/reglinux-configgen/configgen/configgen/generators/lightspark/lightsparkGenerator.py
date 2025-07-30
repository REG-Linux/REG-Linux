from generators.Generator import Generator
from Command import Command

class LightsparkGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["lightspark", "-s", "local-with-networking", rom]
        return Command(
            array=commandArray)

    def getMouseMode(self, config, rom):
        return True
