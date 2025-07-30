from generators.Generator import Generator
from Command import Command
from . import cannonballConfig

class CannonballGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # cannonball config file
        cannonballConfig.setCannonballConfig(system)

        # command line
        commandArray = [cannonballConfig.cannonballBin]

        return Command(array=commandArray)
