from typing import Any

from configgen.controllers import generate_sdl_controller_config
from configgen.core import Command
from configgen.generators.generator import DeviceConfig, Generator

from .iortcwConfig import IORTCW_BIN_PATH, setIortcwConfig


class IORTCWGenerator(Generator):
    def generate(
        self,
        system: Any,
        rom: str,
        players_controllers: Any,
        metadata: Any,
        guns: DeviceConfig,
        wheels: DeviceConfig,
        game_resolution: dict[str, int],
    ) -> Command:
        setIortcwConfig(system, game_resolution)

        # Single Player for now
        command_array = [IORTCW_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )

    def get_in_game_ratio(
        self,
        config: Any,
        game_resolution: dict[str, int],
        rom: str,
    ) -> float:
        return 16 / 9
