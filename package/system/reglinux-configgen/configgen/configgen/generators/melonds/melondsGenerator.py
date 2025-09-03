from generators.Generator import Generator
from Command import Command
from os import path, mkdir
from codecs import open
from .melondsControllers import setMelondsControllers
from .melondsConfig import (
    setMelonDSConfig,
    MELONDS_BIN_PATH,
    MELONDS_SAVES_DIR,
    MELONDS_CHEATS_DIR,
    MELONDS_CONFIG_DIR,
    MELONDS_CONFIG_PATH,
)


class MelonDSGenerator(Generator):
    # this emulator/core requires wayland compositor to run
    def requiresWayland(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Verify the save path exists
        if not path.exists(MELONDS_SAVES_DIR):
            mkdir(MELONDS_SAVES_DIR)

        # Verify the cheat path exist
        if not path.exists(MELONDS_CHEATS_DIR):
            mkdir(MELONDS_CHEATS_DIR)

        # Verify the config path exist
        if not path.exists(MELONDS_CONFIG_DIR):
            mkdir(MELONDS_CONFIG_DIR)

        # Config file
        melondsConfig = open(MELONDS_CONFIG_PATH, "w", encoding="utf_8_sig")

        setMelonDSConfig(melondsConfig, system, gameResolution)
        setMelondsControllers(melondsConfig, playersControllers)

        # Now write the ini file
        melondsConfig.close()

        commandArray = [MELONDS_BIN_PATH, "-f", rom]
        return Command(array=commandArray)
