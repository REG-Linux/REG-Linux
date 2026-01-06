from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import ROMS

ROTT_ROMS_DIR = str(ROMS / "rott")
ROTT_BIN_PATH = "/usr/bin/taradino"


class TaradinoGenerator(Generator):
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
        command_array = [ROTT_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "XDG_DATA_DIRS": ROTT_ROMS_DIR,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
