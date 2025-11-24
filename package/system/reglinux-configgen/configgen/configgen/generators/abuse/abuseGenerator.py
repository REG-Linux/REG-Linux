from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import ROMS

ABUSE_DATA_DIR = ROMS + "/abuse/abuse_data"
ABUSE_BIN_PATH = "/usr/bin/abuse"


class AbuseGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = [ABUSE_BIN_PATH, "-datadir", ABUSE_DATA_DIR]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
