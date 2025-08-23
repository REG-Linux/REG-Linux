from generators.Generator import Generator
from Command import Command
from systemFiles import ROMS
from os import chdir
from controllers import generate_sdl_controller_config

JAZZ2_ROMS_DIR = ROMS + '/jazz2'
JAZZ2_BIN_PATH = '/usr/bin/jazz2'

from utils.logger import get_logger
eslog = get_logger(__name__)

class Jazz2Generator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            chdir(JAZZ2_ROMS_DIR)
        except:
            eslog.error("ERROR: Game assets not installed. You can install your own or get them from the Content Downloader.")

        commandArray = [JAZZ2_BIN_PATH, "-f", JAZZ2_ROMS_DIR + rom]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                    })
