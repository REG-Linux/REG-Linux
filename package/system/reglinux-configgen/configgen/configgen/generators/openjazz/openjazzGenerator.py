from os import chdir

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import ROMS
from configgen.utils.logger import get_logger

OPENJAZZ_ROMS_DIR = str(ROMS / "openjazz")
OPENJAZZ_BIN_PATH = "/usr/bin/OpenJazz"

eslog = get_logger(__name__)


class OpenJazzGenerator(Generator):
    def generate(
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    ):
        try:
            chdir(OPENJAZZ_ROMS_DIR)
        except FileNotFoundError:
            eslog.error(
                f"ERROR: OpenJazz ROMs directory not found: {OPENJAZZ_ROMS_DIR}. Game assets not installed. You can install your own or get them from the Content Downloader.",
            )
        except PermissionError:
            eslog.error(
                f"ERROR: Permission denied accessing OpenJazz ROMs directory: {OPENJAZZ_ROMS_DIR}. Check directory permissions.",
            )
        except OSError as e:
            eslog.error(
                f"ERROR: OS error when changing to OpenJazz ROMs directory {OPENJAZZ_ROMS_DIR}: {e}. Game assets may not be installed.",
            )

        command_array = [OPENJAZZ_BIN_PATH, "-f", OPENJAZZ_ROMS_DIR + rom]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
