from pathlib import Path
from typing import override

from configgen.core import Command
from configgen.generators.generator import Generator
from configgen.settings import UnixSettings

from .azaharConfig import AZAHAR_BIN_PATH, AZAHAR_CONFIG_PATH, setAzaharConfig
from .azaharControllers import setAzaharControllers


class AzaharGenerator(Generator):
    # this emulator/core requires X server to run
    @override
    def requiresX11(self):
        return True

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
        # Remove existing config file to ensure clean state
        config_path = Path(AZAHAR_CONFIG_PATH)
        if config_path.exists():
            config_path.unlink()

        # Load existing config or create a new one
        azaharConfig = UnixSettings(AZAHAR_CONFIG_PATH)

        # Update configuration
        setAzaharConfig(azaharConfig, system)
        setAzaharControllers(azaharConfig, players_controllers)

        # Save the updated configuration
        azaharConfig.write()

        return Command(array=[AZAHAR_BIN_PATH, rom])
