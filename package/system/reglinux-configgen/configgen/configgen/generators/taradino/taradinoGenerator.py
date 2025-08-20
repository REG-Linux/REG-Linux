from Command import Command
from generators.Generator import Generator
from systemFiles import ROMS
from controllers import generate_sdl_controller_config

ROTT_ROMS_DIR = ROMS + '/rott'
ROTT_BIN_PATH = '/usr/bin/taradino'

class TaradinoGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [ ROTT_BIN_PATH ]

        return Command(
            array=commandArray,
            env={
                "XDG_DATA_DIRS": ROTT_ROMS_DIR,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(playersControllers)
            }
        )
