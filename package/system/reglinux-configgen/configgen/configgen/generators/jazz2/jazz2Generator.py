from os import chdir

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import ROMS
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

JAZZ2_ROMS_DIR = ROMS / "jazz2"
JAZZ2_BIN_PATH = "/usr/bin/jazz2"


class Jazz2Generator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        try:
            chdir(JAZZ2_ROMS_DIR)
        except FileNotFoundError:
            eslog.error(
                f"ERROR: Jazz2 ROMs directory not found: {JAZZ2_ROMS_DIR}. Game assets not installed. You can install your own or get them from the Content Downloader.",
            )
        except PermissionError:
            eslog.error(
                f"ERROR: Permission denied accessing Jazz2 ROMs directory: {JAZZ2_ROMS_DIR}. Check directory permissions.",
            )
        except OSError as e:
            eslog.error(
                f"ERROR: OS error when changing to Jazz2 ROMs directory {JAZZ2_ROMS_DIR}: {e}. Game assets may not be installed.",
            )

        command_array = [JAZZ2_BIN_PATH, "-f", str(JAZZ2_ROMS_DIR / rom)]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
