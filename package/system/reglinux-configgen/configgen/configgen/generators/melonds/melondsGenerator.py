from pathlib import Path

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
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        # Verify the save path exists
        saves_dir_path = Path(MELONDS_SAVES_DIR)
        if not saves_dir_path.exists():
            saves_dir_path.mkdir(parents=True, exist_ok=True)

        # Verify the cheat path exist
        cheats_dir_path = Path(MELONDS_CHEATS_DIR)
        if not cheats_dir_path.exists():
            cheats_dir_path.mkdir(parents=True, exist_ok=True)

        melondsConfig = UnixSettings(MELONDS_CONFIG_PATH)

        setMelonDSConfig(melondsConfig, system, game_resolution)
        setMelondsControllers(melondsConfig, players_controllers)

        # Now write the ini file
        melondsConfig.write()

        command_array = [MELONDS_BIN_PATH, "-f", rom]
        return Command(array=command_array)
