from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs
from shutil import copyfile
from configgen.controllers import generate_sdl_controller_config
from .xemuConfig import setXemuConfig, XEMU_BIN_PATH, XEMU_CONFIG_PATH, XEMU_SAVES_DIR


class XemuGenerator(Generator):
    # Main entry of the module
    # Configure fba and return a command
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        setXemuConfig(system, rom, playersControllers, gameResolution)

        # copy the hdd if it doesn't exist
        if not path.exists(XEMU_SAVES_DIR + "/xbox_hdd.qcow2"):
            if not path.exists(XEMU_SAVES_DIR):
                makedirs(XEMU_SAVES_DIR)
            copyfile(
                "/usr/share/xemu/data/xbox_hdd.qcow2",
                XEMU_SAVES_DIR + "/xbox_hdd.qcow2",
            )

        # the command to run
        commandArray = [XEMU_BIN_PATH]
        commandArray.extend(["-config_path", XEMU_CONFIG_PATH])

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if ("xemu_scaling" in config and config["xemu_scaling"] == "stretch") or (
            "xemu_aspect" in config and config["xemu_aspect"] == "16x9"
        ):
            return 16 / 9
        return 4 / 3
