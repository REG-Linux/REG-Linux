from generators.Generator import Generator
from Command import Command
from controllers import generate_sdl_controller_config
from .abuseConfig import ABUSE_BIN_PATH, ABUSE_DATA_DIR

class AbuseGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [ABUSE_BIN_PATH, "-datadir", ABUSE_DATA_DIR]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                    })
