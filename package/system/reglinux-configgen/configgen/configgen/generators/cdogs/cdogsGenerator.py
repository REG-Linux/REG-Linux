from os import chdir

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator

from .cdogsConfig import CDOGS_ASSETS_DIR, CDOGS_BIN_PATH, CDOGS_ROMS_DIR


class CdogsGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        try:
            for assetdir in CDOGS_ASSETS_DIR:
                chdir(f"{CDOGS_ROMS_DIR}/{assetdir}")
            chdir(CDOGS_ROMS_DIR)
        except FileNotFoundError:
            raise

        command_array = [CDOGS_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
