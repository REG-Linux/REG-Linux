from configgen.generators.Generator import Generator
from configgen.Command import Command
from configparser import ConfigParser
from os import path, makedirs
from .mupenConfig import (
    setMupenConfig,
    MUPEN_CONFIG_PATH,
    MUPEN_BIN_PATH,
    MUPEN_CONFIG_DIR,
)


class MupenGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Read the configuration file
        iniConfig = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = lambda optionstr: str(optionstr)
        if path.exists(MUPEN_CONFIG_PATH):
            iniConfig.read(MUPEN_CONFIG_PATH)
        else:
            if not path.exists(path.dirname(MUPEN_CONFIG_PATH)):
                makedirs(path.dirname(MUPEN_CONFIG_PATH))
            iniConfig.read(MUPEN_CONFIG_PATH)

        setMupenConfig(iniConfig, system, playersControllers, gameResolution)

        # Save the ini file
        if not path.exists(path.dirname(MUPEN_CONFIG_PATH)):
            makedirs(path.dirname(MUPEN_CONFIG_PATH))
        with open(MUPEN_CONFIG_PATH, "w") as configfile:
            iniConfig.write(configfile)

        # Command
        commandArray = [
            MUPEN_BIN_PATH,
            "--plugindir",
            "/usr/lib/mupen64plus/",
            "--corelib",
            "libmupen64plus.so.2.0.0",
            "--gfx",
            "mupen64plus-video-{}.so".format(system.config["core"]),
            "--audio",
            "mupen64plus-audio-sdl.so",
            "--input",
            "mupen64plus-input-sdl.so",
            "--rsp",
            "mupen64plus-rsp-hle.so",
            "--configdir",
            MUPEN_CONFIG_DIR,
            "--datadir",
            MUPEN_CONFIG_DIR,
        ]

        # state_slot option
        if system.isOptSet("state_filename"):
            commandArray.extend(["--savestate", system.config["state_filename"]])

        commandArray.append(rom)

        return Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if (
            "mupen64plus_ratio" in config and config["mupen64plus_ratio"] == "16/9"
        ) or (
            "mupen64plus_ratio" not in config
            and "ratio" in config
            and config["ratio"] == "16/9"
        ):
            return 16 / 9
        return 4 / 3
