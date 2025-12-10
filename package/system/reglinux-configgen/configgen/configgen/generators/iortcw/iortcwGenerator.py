from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from .iortcwConfig import setIortcwConfig, IORTCW_BIN_PATH


class IORTCWGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        setIortcwConfig(system, game_resolution)

        # Single Player for now
        command_array = [IORTCW_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    def get_in_game_ratio(self, config, game_resolution, rom):
        return 16 / 9
