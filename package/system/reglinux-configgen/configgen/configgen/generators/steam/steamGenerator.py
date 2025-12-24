from os import path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator


class SteamGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        basename = path.basename(rom)
        gameId = None
        if basename != "Steam.steam":
            # read the id inside the file
            with open(rom) as f:
                gameId = str.strip(f.read())

        if gameId is None:
            command_array = ["batocera-steam"]
        else:
            command_array = ["batocera-steam", gameId]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    def getMouseMode(self, config, rom):
        return True
