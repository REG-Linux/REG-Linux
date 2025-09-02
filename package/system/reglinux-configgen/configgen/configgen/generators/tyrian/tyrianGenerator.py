from generators.Generator import Generator
from Command import Command
from os import chdir
from systemFiles import ROMS
from controllers import generate_sdl_controller_config

TYRIAN_ROMS_DIR = ROMS + "tyrian/data"
TYRIAN_BIN_PATH = "/usr/bin/opentyrian"

from utils.logger import get_logger

eslog = get_logger(__name__)


class TyrianGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        try:
            chdir(TYRIAN_ROMS_DIR)
        except:
            eslog.error(
                "ERROR: Game assets not installed. You can get them from the Batocera Content Downloader."
            )
        commandArray = [TYRIAN_BIN_PATH]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
