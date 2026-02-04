from pathlib import Path
from shutil import copyfile
from typing import Any

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator

from .xemuConfig import XEMU_BIN_PATH, XEMU_CONFIG_PATH, XEMU_SAVES_DIR, setXemuConfig


class XemuGenerator(Generator):
    # Main entry of the module
    # Configure fba and return a command
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
        setXemuConfig(system, rom, players_controllers, game_resolution)

        # copy the hdd if it doesn't exist
        hdd_path = Path(XEMU_SAVES_DIR) / "xbox_hdd.qcow2"
        if not hdd_path.exists():
            saves_dir_path = Path(XEMU_SAVES_DIR)
            if not saves_dir_path.exists():
                saves_dir_path.mkdir(parents=True, exist_ok=True)
            copyfile(
                "/usr/share/xemu/data/xbox_hdd.qcow2",
                str(hdd_path),
            )

        # the command to run
        command_array = [str(XEMU_BIN_PATH)]
        command_array.extend(["-config_path", str(XEMU_CONFIG_PATH)])

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
        if ("xemu_scaling" in config and config["xemu_scaling"] == "stretch") or (
            "xemu_aspect" in config and config["xemu_aspect"] == "16x9"
        ):
            return 16 / 9
        return 4 / 3
