from configgen.command import Command
from configgen.generators.generator import Generator
from configgen.settings import UnixSettings

from .azaharConfig import AZAHAR_BIN_PATH, AZAHAR_CONFIG_PATH, setAzaharConfig
from .azaharControllers import setAzaharControllers


class AzaharGenerator(Generator):
    # this emulator/core requires X server to run
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
        # Load existing config or create a new one
        azaharConfig = UnixSettings(AZAHAR_CONFIG_PATH)

        # Update configuration
        setAzaharConfig(azaharConfig, system)
        # TODO: Set controllers
        setAzaharControllers(azaharConfig, players_controllers)

        # Save the updated configuration
        azaharConfig.write()  # UnixSettings method

        command_array = [AZAHAR_BIN_PATH, rom]
        return Command(array=command_array)
