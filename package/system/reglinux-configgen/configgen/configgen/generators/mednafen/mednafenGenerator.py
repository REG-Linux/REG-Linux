from pathlib import Path

from configgen.command import Command
from configgen.generators.generator import Generator

from .mednafenConfig import (
    MEDNAFEN_BIN_PATH,
    MEDNAFEN_CONFIG_DIR,
    MEDNAFEN_CONFIG_PATH,
    setMednafenConfig,
)
from .mednafenControllers import setMednafenControllers


class MednafenGenerator(Generator):
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
        config_dir_path = Path(MEDNAFEN_CONFIG_DIR)
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)

        # If config file already exists, delete it
        config_path = Path(MEDNAFEN_CONFIG_PATH)
        if config_path.exists():
            config_path.unlink()

        # Create the config file and fill it with basic data
        with Path(MEDNAFEN_CONFIG_PATH).open("w") as cfgConfig:
            # Basic settings
            setMednafenConfig(cfgConfig)
            # TODO: Controls configuration
            setMednafenControllers(cfgConfig)

        command_array = [MEDNAFEN_BIN_PATH, rom]
        return Command(array=command_array)
