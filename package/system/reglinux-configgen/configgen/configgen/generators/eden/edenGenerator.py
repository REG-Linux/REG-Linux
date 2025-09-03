from generators.Generator import Generator
from Command import Command
from settings import UnixSettings
from .edenController import setEdenControllers
from .edenConfig import setEdenConfig, EDEN_BIN_PATH, EDEN_CONFIG_PATH


class EdenGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Load existing config or create a new one
        edenConfig = UnixSettings(EDEN_CONFIG_PATH)

        setEdenConfig(edenConfig, system)
        setEdenControllers(edenConfig, system, playersControllers)

        # Save the updated configuration
        edenConfig.write()  # UnixSettings method

        commandArray = [EDEN_BIN_PATH, "-f", "-g", rom]
        return Command(array=commandArray)
