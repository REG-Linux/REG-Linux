from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.settings import UnixSettings

from .edenConfig import EDEN_BIN_PATH, EDEN_CONFIG_PATH, setEdenConfig
from .edenController import setEdenControllers


class EdenGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Load existing config or create a new one
        edenConfig = UnixSettings(EDEN_CONFIG_PATH)

        setEdenConfig(edenConfig, system)
        setEdenControllers(edenConfig, system, players_controllers)

        # Save the updated configuration
        edenConfig.write()  # UnixSettings method

        command_array = [EDEN_BIN_PATH, "-f", "-g", rom]
        return Command(array=command_array)
