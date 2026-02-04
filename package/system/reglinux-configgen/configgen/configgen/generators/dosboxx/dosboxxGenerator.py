from configparser import ConfigParser
from pathlib import Path
from shutil import copy2

from configgen.command import Command
from configgen.generators.generator import Generator
from configgen.systemFiles import CONF

DOSBOXX_CONFIG_DIR = str(Path(CONF) / "dosbox")
DOSBOXX_CONFIG_PATH = str(Path(DOSBOXX_CONFIG_DIR) / "dosboxx.conf")
DOSBOXX_CONFIG_CUSTOM_PATH = str(Path(DOSBOXX_CONFIG_DIR) / "dosboxx-custom.conf")
DOSBOXX_BIN_PATH = "/usr/bin/dosbox-x"


class DosBoxxGenerator(Generator):
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
        # Find rom path
        gameDir = rom
        gameConfFile = str(Path(gameDir) / "dosbox.cfg")
        config_file = DOSBOXX_CONFIG_PATH

        config_path = Path(DOSBOXX_CONFIG_PATH)
        if not config_path.parent.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)

        game_conf_file = Path(gameConfFile)
        if game_conf_file.is_file():
            config_file = gameConfFile

        # configuration file
        iniSettings = ConfigParser(interpolation=None)
        iniSettings.optionxform = lambda optionstr: str(optionstr)

        config_file_path = Path(config_file)
        if config_file_path.exists():
            copy2(config_file, DOSBOXX_CONFIG_CUSTOM_PATH)
            iniSettings.read(DOSBOXX_CONFIG_CUSTOM_PATH)

        # sections
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # save
        with Path(DOSBOXX_CONFIG_CUSTOM_PATH).open("w") as config:
            iniSettings.write(config)

        command_array = [
            DOSBOXX_BIN_PATH,
            "-exit",
            "-c",
            f"""mount c {gameDir}""",
            "-c",
            "c:",
            "-c",
            "dosbox.bat",
            "-fastlaunch",
            "-fullscreen",
            "-nogui",
            f"-conf {DOSBOXX_CONFIG_CUSTOM_PATH}",
        ]

        return Command(array=command_array)
