from os import chdir
from typing import Any

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import ROMS
from configgen.utils.logger import get_logger

TYRIAN_ROMS_DIR = str(ROMS / "tyrian" / "data")
TYRIAN_BIN_PATH = "/usr/bin/opentyrian"

eslog = get_logger(__name__)


class TyrianGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
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
        command_array = [TYRIAN_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    def get_in_game_ratio(
        self, config: Any, game_resolution: dict[str, int], rom: str
    ) -> float:
        return 16 / 9
