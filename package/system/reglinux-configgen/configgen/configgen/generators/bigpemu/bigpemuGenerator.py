from os import makedirs, path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.settings import JSONSettings

from .bigpemuConfig import (
    BIGPEMU_BIN_PATH,
    BIGPEMU_CONFIG_DIR,
    BIGPEMU_CONFIG_PATH,
    setBigemuConfig,
)


class BigPEmuGenerator(Generator):
    def generate(
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    ):
        # Create the directory if it doesn't exist
        if not path.exists(BIGPEMU_CONFIG_DIR):
            makedirs(BIGPEMU_CONFIG_DIR)

        # Load existing configuration or create a new one
        bigpemuConfig = JSONSettings(BIGPEMU_CONFIG_PATH)

        # Update configuration
        setBigemuConfig(bigpemuConfig, system, game_resolution, players_controllers)

        # Save the updated configuration
        bigpemuConfig.write()

        command_array = [BIGPEMU_BIN_PATH, rom]
        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
