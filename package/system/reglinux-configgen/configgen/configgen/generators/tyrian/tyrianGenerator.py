from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import chdir
from configgen.systemFiles import ROMS
from configgen.controllers import generate_sdl_controller_config

TYRIAN_ROMS_DIR = ROMS + "tyrian/data"
TYRIAN_BIN_PATH = "/usr/bin/opentyrian"

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class TyrianGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        try:
            chdir(TYRIAN_ROMS_DIR)
        except FileNotFoundError:
            eslog.error(
                f"ERROR: Tyrian ROMs directory not found: {TYRIAN_ROMS_DIR}. Game assets not installed. You can get them from the Batocera Content Downloader."
            )
        except PermissionError:
            eslog.error(
                f"ERROR: Permission denied accessing Tyrian ROMs directory: {TYRIAN_ROMS_DIR}. Check directory permissions."
            )
        except OSError as e:
            eslog.error(
                f"ERROR: OS error when changing to Tyrian ROMs directory {TYRIAN_ROMS_DIR}: {e}. Game assets may not be installed."
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
