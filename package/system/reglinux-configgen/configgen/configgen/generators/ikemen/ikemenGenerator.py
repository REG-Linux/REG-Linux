from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.settings import JSONSettings
from .ikemenControllers import Keymapping, Joymapping

IKEMEN_CONFIG_PATH = "/save/config.json"
IKEMEN_BIN_PATH = "/usr/bin/system-ikemen"


class IkemenGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Load existing config or create a new one
        ikemenConfig = JSONSettings(rom + IKEMEN_CONFIG_PATH)

        # Joystick configuration seems completely broken in 0.98.2 Linux
        # so let's force keyboad and use a pad2key
        ikemenConfig["KeyConfig"] = Keymapping
        ikemenConfig["JoystickConfig"] = Joymapping
        ikemenConfig["Fullscreen"] = True

        # Save the updated configuration
        ikemenConfig.write()

        commandArray = [IKEMEN_BIN_PATH, rom]

        return Command(array=commandArray)
