from os import chdir
from pathlib import Path

from configgen.config.paths import BIOS, ROMS
from configgen.controllers import generate_sdl_controller_config
from configgen.core import Command
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

OPENLARA_ROMS_DIR = str(ROMS / "openlara")
OPENLARA_BIOS_DIR = str(BIOS / "openlara")
OPENLARA_BIN_PATH = "/usr/bin/OpenLara"

eslog = get_logger(__name__)


class OpenLaraGenerator(Generator):
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
        # Change to the OpenLara BIOS directory to ensure proper execution
        bios_dir = Path(OPENLARA_BIOS_DIR)
        if bios_dir.exists():
            try:
                chdir(bios_dir)
            except (PermissionError, OSError) as e:
                eslog.warning(
                    f"Could not change to OpenLara BIOS directory {OPENLARA_BIOS_DIR}: {e}",
                )

        # Construct the command to run OpenLara with the specified ROM
        command_array = [OPENLARA_BIN_PATH, rom]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
