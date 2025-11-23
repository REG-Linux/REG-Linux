from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import HOME

APPLEWIN_CONFIG_PATH = HOME + "/applewin/applewin.conf"
APPLEWIN_BIN_PATH = "/usr/bin/applewin"


class AppleWinGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = [APPLEWIN_BIN_PATH, "--no-imgui", "--d1", rom]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
