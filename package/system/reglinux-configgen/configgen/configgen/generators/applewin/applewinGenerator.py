from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import HOME

APPLEWIN_CONFIG_PATH = HOME + "/applewin/applewin.conf"
APPLEWIN_BIN_PATH = "/usr/bin/applewin"


class AppleWinGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        command_array = [APPLEWIN_BIN_PATH, "--no-imgui", "--d1", rom]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
