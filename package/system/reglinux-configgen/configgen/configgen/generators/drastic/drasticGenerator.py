from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, chdir
from shutil import copytree
from configgen.controllers import generate_sdl_controller_config
from .drasticControllers import setDrasticController
from .drasticConfig import (
    DRASTIC_CONFIG_DIR,
    DRASTIC_CONFIG_DIR_USER,
    DRASTIC_CONFIG_PATH,
    DRASTIC_BIN_PATH,
    setDrasticConfig,
)


class DrasticGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Create the config directory if it doesn't exist
        if not path.exists(DRASTIC_CONFIG_DIR_USER):
            copytree(DRASTIC_CONFIG_DIR, DRASTIC_CONFIG_DIR_USER)

        drasticConfig = open(DRASTIC_CONFIG_PATH, "w", encoding="ascii")
        setDrasticConfig(drasticConfig, system)
        setDrasticController(drasticConfig)
        drasticConfig.close()

        chdir(DRASTIC_CONFIG_DIR_USER)
        command_array = [DRASTIC_BIN_PATH, rom]
        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
