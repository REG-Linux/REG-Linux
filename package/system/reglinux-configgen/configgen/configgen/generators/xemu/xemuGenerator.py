from os import makedirs, path
from shutil import copyfile

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator

from .xemuConfig import XEMU_BIN_PATH, XEMU_CONFIG_PATH, XEMU_SAVES_DIR, setXemuConfig


class XemuGenerator(Generator):
    # Main entry of the module
    # Configure fba and return a command
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        setXemuConfig(system, rom, players_controllers, game_resolution)

        # copy the hdd if it doesn't exist
        if not path.exists(XEMU_SAVES_DIR + "/xbox_hdd.qcow2"):
            if not path.exists(XEMU_SAVES_DIR):
                makedirs(XEMU_SAVES_DIR)
            copyfile(
                "/usr/share/xemu/data/xbox_hdd.qcow2",
                XEMU_SAVES_DIR + "/xbox_hdd.qcow2",
            )

        # the command to run
        command_array = [XEMU_BIN_PATH]
        command_array.extend(["-config_path", XEMU_CONFIG_PATH])

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    def get_in_game_ratio(self, config, game_resolution, rom):
        if ("xemu_scaling" in config and config["xemu_scaling"] == "stretch") or (
            "xemu_aspect" in config and config["xemu_aspect"] == "16x9"
        ):
            return 16 / 9
        return 4 / 3
