from configgen.generators.Generator import Generator
from configgen.Command import Command
from configparser import ConfigParser
from os import path, makedirs
from shutil import copy2
from configgen.systemFiles import CONF

DOSBOXX_CONFIG_DIR = CONF + "/dosbox"
DOSBOXX_CONFIG_PATH = DOSBOXX_CONFIG_DIR + "/dosboxx.conf"
DOSBOXX_CONFIG_CUSTOM_PATH = DOSBOXX_CONFIG_DIR + "/dosboxx-custom.conf"
DOSBOXX_BIN_PATH = "/usr/bin/dosbox-x"


class DosBoxxGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Find rom path
        gameDir = rom
        gameConfFile = gameDir + "/dosbox.cfg"
        configFile = DOSBOXX_CONFIG_PATH

        if not path.exists(path.dirname(DOSBOXX_CONFIG_PATH)):
            makedirs(path.dirname(DOSBOXX_CONFIG_PATH))

        if path.isfile(gameConfFile):
            configFile = gameConfFile

        # configuration file
        iniSettings = ConfigParser(interpolation=None)
        iniSettings.optionxform = lambda optionstr: str(optionstr)

        if path.exists(configFile):
            copy2(configFile, DOSBOXX_CONFIG_CUSTOM_PATH)
            iniSettings.read(DOSBOXX_CONFIG_CUSTOM_PATH)

        # sections
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # save
        with open(DOSBOXX_CONFIG_CUSTOM_PATH, "w") as config:
            iniSettings.write(config)

        commandArray = [
            DOSBOXX_BIN_PATH,
            "-exit",
            "-c",
            f"""mount c {gameDir}""",
            "-c",
            "c:",
            "-c",
            "dosbox.bat",
            "-fastbioslogo",
            "-fullscreen",
            f"-conf {DOSBOXX_CONFIG_CUSTOM_PATH}",
        ]

        return Command(array=commandArray)
