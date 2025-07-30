from generators.Generator import Generator
from Command import Command
import controllers as controllersConfig
from . import abuseConfig

class AbuseGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = [abuseConfig.abuseBin, "-datadir", abuseConfig.abuseDataDir]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generate_sdl_controller_config(playersControllers)
                    })
