from generators.Generator import Generator
from Command import Command
from settings import UnixSettings
from .azaharConfig import setAzaharConfig, AZAHAR_BIN_PATH, AZAHAR_CONFIG_PATH
from .azaharControllers import setAzaharControllers


class AzaharGenerator(Generator):
    # this emulator/core requires X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Load existing config or create a new one
        azaharConfig = UnixSettings(AZAHAR_CONFIG_PATH)

        # Update configuration
        setAzaharConfig(azaharConfig, system)
        # TODO: Set controllers
        setAzaharControllers(azaharConfig, playersControllers)

        # Save the updated configuration
        azaharConfig.write()  # UnixSettings method

        commandArray = [AZAHAR_BIN_PATH, rom]
        return Command(array=commandArray)
