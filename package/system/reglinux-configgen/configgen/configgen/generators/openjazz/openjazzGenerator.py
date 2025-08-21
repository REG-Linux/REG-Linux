from generators.Generator import Generator
from Command import Command
from systemFiles import ROMS
from os import chdir
from controllers import generate_sdl_controller_config

OPENJAZZ_ROMS_DIR = ROMS + '/openjazz'
OPENJAZZ_BIN_PATH = '/usr/bin/OpenJazz'

from utils.logger import get_logger
eslog = get_logger(__name__)

class OpenJazzGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            chdir(OPENJAZZ_ROMS_DIR)
        except:
            eslog.error("ERROR: Game assets not installed. You can install your own or get them from the Content Downloader.")

        commandArray = [OPENJAZZ_BIN_PATH, "-f", OPENJAZZ_ROMS_DIR + rom]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                    })
