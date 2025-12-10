from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.systemFiles import ROMS
from os import chdir
from configgen.controllers import generate_sdl_controller_config

OPENJAZZ_ROMS_DIR = ROMS + "/openjazz"
OPENJAZZ_BIN_PATH = "/usr/bin/OpenJazz"

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class OpenJazzGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        try:
            chdir(OPENJAZZ_ROMS_DIR)
        except FileNotFoundError:
            eslog.error(
                f"ERROR: OpenJazz ROMs directory not found: {OPENJAZZ_ROMS_DIR}. Game assets not installed. You can install your own or get them from the Content Downloader."
            )
        except PermissionError:
            eslog.error(
                f"ERROR: Permission denied accessing OpenJazz ROMs directory: {OPENJAZZ_ROMS_DIR}. Check directory permissions."
            )
        except OSError as e:
            eslog.error(
                f"ERROR: OS error when changing to OpenJazz ROMs directory {OPENJAZZ_ROMS_DIR}: {e}. Game assets may not be installed."
            )

        commandArray = [OPENJAZZ_BIN_PATH, "-f", OPENJAZZ_ROMS_DIR + rom]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
