import pathlib

from configgen.controllers import generate_sdl_controller_config
from configgen.core import Command
from configgen.generators.generator import Generator
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
        if not pathlib.Path(BIGPEMU_CONFIG_DIR).exists():
            pathlib.Path(BIGPEMU_CONFIG_DIR).mkdir(parents=True)

        # Remove existing config file to ensure clean state (no dynamic values)
        config_path = pathlib.Path(BIGPEMU_CONFIG_PATH)
        if config_path.exists():
            config_path.unlink()

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
