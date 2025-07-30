from Command import Command
from generators.Generator import Generator

class TaradinoGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [ "taradino" ]

        return Command(
            array=commandArray,
            env={
                "XDG_DATA_DIRS": "/userdata/roms/rott"
            }
        )
