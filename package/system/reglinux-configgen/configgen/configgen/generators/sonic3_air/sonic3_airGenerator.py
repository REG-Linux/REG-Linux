from json import dump, load
from pathlib import Path
from shutil import copy
from typing import Any

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF, SAVES

SONIC3AIR_CONFIG_PATH = "/usr/bin/sonic3-air/config.json"
SONIC3AIR_OXIGEN_PATH = "/usr/bin/sonic3-air/oxygenproject.json"
SONIC3AIR_CONFIG_DIR = str(CONF / "Sonic3AIR")
SONIC3AIR_DEST_CONFIG_PATH = str(CONF / "Sonic3AIR" / "config.json")
SONIC3AIR_DEST_OXIGEN_PATH = str(CONF / "Sonic3AIR" / "oxygenproject.json")
SONIC3AIR_SAVES_DIR = str(SAVES / "sonic3-air")
SONIC3AIR_SETTINGS_PATH = str(CONF / "Sonic3AIR" / "settings.json")
SONIC3AIR_BIN_PATH = "/usr/bin/sonic3-air/sonic3air_linux"


class Sonic3AIRGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # copy configuration json files so we can manipulate them
        config_dest_path = Path(SONIC3AIR_DEST_CONFIG_PATH)
        if not config_dest_path.exists():
            config_dir_path = Path(SONIC3AIR_CONFIG_DIR)
            if not config_dir_path.exists():
                config_dir_path.mkdir(parents=True, exist_ok=True)
            copy(SONIC3AIR_CONFIG_PATH, SONIC3AIR_DEST_CONFIG_PATH)
        oxigen_dest_path = Path(SONIC3AIR_DEST_OXIGEN_PATH)
        if not oxigen_dest_path.exists():
            config_dir_path = Path(SONIC3AIR_CONFIG_DIR)
            if not config_dir_path.exists():
                config_dir_path.mkdir(parents=True, exist_ok=True)
            copy(SONIC3AIR_OXIGEN_PATH, SONIC3AIR_DEST_OXIGEN_PATH)

        # saves dir
        saves_dir_path = Path(SONIC3AIR_SAVES_DIR)
        if not saves_dir_path.exists():
            saves_dir_path.mkdir(parents=True, exist_ok=True)

        # read the json file
        # can't use `import json` as the file is not compliant
        with open(SONIC3AIR_DEST_CONFIG_PATH) as file:
            json_text = file.read()
        # update the "SaveStatesDir"
        json_text = json_text.replace(
            '"SaveStatesDir":  "saves/states"',
            '"SaveStatesDir":  "/userdata/saves/sonic3-air"',
        )

        # extract the current resolution value
        current_resolution = json_text.split('"WindowSize": "')[1].split('"')[0]
        # replace the resolution with new values
        new_resolution = (
            str(game_resolution["width"]) + " x " + str(game_resolution["height"])
        )
        json_text = json_text.replace(
            f'"WindowSize": "{current_resolution}"', f'"WindowSize": "{new_resolution}"'
        )

        with open(SONIC3AIR_DEST_CONFIG_PATH, "w") as file:
            file.write(json_text)

        # settings json - compliant
        # ensure fullscreen
        settings_path = Path(SONIC3AIR_SETTINGS_PATH)
        if settings_path.exists():
            with open(SONIC3AIR_SETTINGS_PATH) as file:
                settings_data = load(file)
                settings_data["Fullscreen"] = 1
        else:
            settings_data = {"Fullscreen": 1}

        with open(SONIC3AIR_SETTINGS_PATH, "w") as file:
            dump(settings_data, file, indent=4)

        # now run
        command_array = [SONIC3AIR_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return False

    def get_in_game_ratio(
        self, config: Any, game_resolution: dict[str, int], rom: str
    ) -> float:
        return 16 / 9
