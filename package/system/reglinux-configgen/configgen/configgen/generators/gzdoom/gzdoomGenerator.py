from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, mkdir
from shlex import split
from .gzdoomControllers import setGzdoomControllers
from .gzdoomConfig import (
    setGzdoomConfig,
    GZDOOM_CONFIG_DIR,
    GZDOOM_SCRIPT_PATH,
    GZDOOM_SOUND_FONT_PATH,
    GZDOOM_FM_BANKS_PATH,
)


class GZDoomGenerator(Generator):
    # this emulator/core requires wayland compositor to run
    def requiresWayland(self):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # check directories exist
        if not path.exists(GZDOOM_CONFIG_DIR):
            mkdir(GZDOOM_CONFIG_DIR)

        if not path.exists(GZDOOM_SOUND_FONT_PATH):
            mkdir(GZDOOM_SOUND_FONT_PATH)

        if not path.exists(GZDOOM_FM_BANKS_PATH):
            mkdir(GZDOOM_FM_BANKS_PATH)

        setGzdoomConfig(system, rom)
        setGzdoomControllers(system)

        # define how wads are loaded
        # if we use a custom extension use that instead
        if rom.endswith(".gzdoom"):
            with open(rom, "r") as f:
                iwad_command = f.read().strip()
            args = split(iwad_command)
            return Command(
                array=[
                    "gzdoom",
                    *args,
                    "-exec",
                    GZDOOM_SCRIPT_PATH,
                    "-width",
                    str(gameResolution["width"]),
                    "-height",
                    str(gameResolution["height"]),
                    "-nologo" if system.getOptBoolean("nologo") else "",
                ]
            )
        else:
            return Command(
                array=[
                    "gzdoom",
                    "-iwad",
                    path.basename(rom),
                    "-exec",
                    GZDOOM_SCRIPT_PATH,
                    "-width",
                    str(gameResolution["width"]),
                    "-height",
                    str(gameResolution["height"]),
                    "-nologo" if system.getOptBoolean("nologo") else "",
                ]
            )
