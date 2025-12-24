from os import mkdir, path

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.settings import UnixSettings

from .melondsConfig import (
    MELONDS_BIN_PATH,
    MELONDS_CHEATS_DIR,
    MELONDS_CONFIG_PATH,
    MELONDS_SAVES_DIR,
    setMelonDSConfig,
)
from .melondsControllers import setMelondsControllers


class MelonDSGenerator(Generator):
    # this emulator/core requires wayland compositor to run
    def requiresWayland(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Verify the save path exists
        if not path.exists(MELONDS_SAVES_DIR):
            mkdir(MELONDS_SAVES_DIR)

        # Verify the cheat path exist
        if not path.exists(MELONDS_CHEATS_DIR):
            mkdir(MELONDS_CHEATS_DIR)

        melondsConfig = UnixSettings(MELONDS_CONFIG_PATH)

        setMelonDSConfig(melondsConfig, system, game_resolution)
        setMelondsControllers(melondsConfig, players_controllers)

        # Now write the ini file
        melondsConfig.write()

        command_array = [MELONDS_BIN_PATH, "-f", rom]
        return Command(array=command_array)
