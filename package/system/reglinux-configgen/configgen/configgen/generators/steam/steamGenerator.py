from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path
from configgen.controllers import generate_sdl_controller_config


class SteamGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        basename = path.basename(rom)
        gameId = None
        if basename != "Steam.steam":
            # read the id inside the file
            with open(rom) as f:
                gameId = str.strip(f.read())

        if gameId is None:
            commandArray = ["batocera-steam"]
        else:
            commandArray = ["batocera-steam", gameId]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    def getMouseMode(self, config, rom):
        return True
