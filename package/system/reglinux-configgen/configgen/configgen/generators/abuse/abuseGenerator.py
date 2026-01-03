from pathlib import Path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import ROMS

ABUSE_DATA_DIR = ROMS / "abuse" / "abuse_data"
ABUSE_BIN_PATH = Path("/usr/bin/abuse")


class AbuseGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        command_array = [str(ABUSE_BIN_PATH), "-datadir", str(ABUSE_DATA_DIR)]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
