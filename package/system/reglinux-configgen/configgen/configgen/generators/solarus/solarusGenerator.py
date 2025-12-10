from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config

SOLARUS_BIN_PATH = "/usr/bin/solarus-run"


class SolarusGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # basis
        commandArray = [
            SOLARUS_BIN_PATH,
            "-fullscreen=yes",
            "-cursor-visible=no",
            "-lua-console=no",
        ]

        # rom
        commandArray.append(rom)

        return Command(
            array=commandArray,
            env={
                "SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS": "0",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                ),
            },
        )
