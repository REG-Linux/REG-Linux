from os import chdir, path
from shutil import copytree

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator

from .drasticConfig import (
    DRASTIC_BIN_PATH,
    DRASTIC_CONFIG_DIR,
    DRASTIC_CONFIG_DIR_USER,
    DRASTIC_CONFIG_PATH,
    setDrasticConfig,
)
from .drasticControllers import setDrasticController


class DrasticGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Create the config directory if it doesn't exist
        if not path.exists(DRASTIC_CONFIG_DIR_USER):
            copytree(DRASTIC_CONFIG_DIR, DRASTIC_CONFIG_DIR_USER)

        with open(DRASTIC_CONFIG_PATH, "w", encoding="ascii") as drasticConfig:
            setDrasticConfig(drasticConfig, system)
            setDrasticController(drasticConfig)

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
