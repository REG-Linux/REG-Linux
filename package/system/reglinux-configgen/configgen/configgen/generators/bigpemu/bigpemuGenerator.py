from generators.Generator import Generator
from Command import Command
from . import bigpemuConfig

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        bigpemuConfig.readWriteFile(system, gameResolution, playersControllers)

        commandArray = [bigpemuConfig.bigpemuBin, rom]
        return Command(array=commandArray)
