import pathlib
from os import path
from shlex import split
from typing import Any

from configgen.command import Command
from configgen.generators.generator import Generator

from .gzdoomConfig import (
    GZDOOM_CONFIG_DIR,
    GZDOOM_FM_BANKS_PATH,
    GZDOOM_SCRIPT_PATH,
    GZDOOM_SOUND_FONT_PATH,
    setGzdoomConfig,
)
from .gzdoomControllers import setGzdoomControllers


class GZDoomGenerator(Generator):
    # this emulator/core requires wayland compositor to run
    def requiresWayland(self):
        return True

    def get_in_game_ratio(
        self,
        config: Any,
        game_resolution: dict[str, int],
        rom: str,
    ) -> float:
        return 16 / 9

    def generate(
        self,
        system: Any,
        rom: str,
        players_controllers: Any,
        metadata: Any,
        guns: Any,
        wheels: Any,
        game_resolution: dict[str, int],
    ) -> Command:
        # check directories exist
        if not pathlib.Path(GZDOOM_CONFIG_DIR).exists():
            pathlib.Path(GZDOOM_CONFIG_DIR).mkdir()

        if not pathlib.Path(GZDOOM_SOUND_FONT_PATH).exists():
            pathlib.Path(GZDOOM_SOUND_FONT_PATH).mkdir()

        if not pathlib.Path(GZDOOM_FM_BANKS_PATH).exists():
            pathlib.Path(GZDOOM_FM_BANKS_PATH).mkdir()

        setGzdoomConfig(system, rom)
        setGzdoomControllers(system)

        # define how wads are loaded
        # if we use a custom extension use that instead
        if rom.endswith(".gzdoom"):
            with pathlib.Path(rom).open() as f:
                iwad_command = f.read().strip()
            args = split(iwad_command)
            return Command(
                array=[
                    "gzdoom",
                    *args,
                    "-exec",
                    GZDOOM_SCRIPT_PATH,
                    "-width",
                    str(game_resolution["width"]),
                    "-height",
                    str(game_resolution["height"]),
                    "-nologo" if system.getOptBoolean("nologo") else "",
                ],
            )
        return Command(
            array=[
                "gzdoom",
                "-iwad",
                path.basename(rom),
                "-exec",
                GZDOOM_SCRIPT_PATH,
                "-width",
                str(game_resolution["width"]),
                "-height",
                str(game_resolution["height"]),
                "-nologo" if system.getOptBoolean("nologo") else "",
            ],
        )
