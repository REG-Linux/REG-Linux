from generators.Generator import Generator
from Command import Command
from os import path, makedirs
from shutil import copy
from json import load, dump
from controllers import generate_sdl_controller_config
from systemFiles import CONF, SAVES

SONIC3AIR_CONFIG_PATH = '/usr/bin/sonic3-air/config.json'
SONIC3AIR_OXIGEN_PATH = '/usr/bin/sonic3-air/oxygenproject.json'
SONIC3AIR_CONFIG_DIR = CONF + '/Sonic3AIR'
SONIC3AIR_DEST_CONFIG_PATH = SONIC3AIR_CONFIG_DIR + '/config.json'
SONIC3AIR_DEST_OXIGEN_PATH = SONIC3AIR_CONFIG_DIR + '/oxygenproject.json'
SONIC3AIR_SAVES_DIR = SAVES + '/sonic3-air'
SONIC3AIR_SETTINGS_PATH = SONIC3AIR_CONFIG_DIR + '/settings.json'
SONIC3AIR_BIN_PATH = '/usr/bin/sonic3-air/sonic3air_linux'

class Sonic3AIRGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # copy configuration json files so we can manipulate them
        if not path.exists(SONIC3AIR_DEST_CONFIG_PATH):
            if not path.exists(SONIC3AIR_CONFIG_DIR):
                makedirs(SONIC3AIR_CONFIG_DIR)
            copy(SONIC3AIR_CONFIG_PATH, SONIC3AIR_DEST_CONFIG_PATH)
        if not path.exists(SONIC3AIR_DEST_OXIGEN_PATH):
            if not path.exists(SONIC3AIR_CONFIG_DIR):
                makedirs(SONIC3AIR_CONFIG_DIR)
            copy(SONIC3AIR_OXIGEN_PATH, SONIC3AIR_DEST_OXIGEN_PATH)

        # saves dir
        if not path.exists(SONIC3AIR_SAVES_DIR):
                makedirs(SONIC3AIR_SAVES_DIR)

        # read the json file
        # can't use `import json` as the file is not compliant
        with open(SONIC3AIR_DEST_CONFIG_PATH, 'r') as file:
            json_text = file.read()
        # update the "SaveStatesDir"
        json_text = json_text.replace('"SaveStatesDir":  "saves/states"', '"SaveStatesDir":  "/userdata/saves/sonic3-air"')

        # extract the current resolution value
        current_resolution = json_text.split('"WindowSize": "')[1].split('"')[0]
        # replace the resolution with new values
        new_resolution = str(gameResolution["width"]) + " x " + str(gameResolution["height"])
        json_text = json_text.replace(f'"WindowSize": "{current_resolution}"', f'"WindowSize": "{new_resolution}"')

        with open(SONIC3AIR_DEST_CONFIG_PATH, 'w') as file:
            file.write(json_text)

        # settings json - compliant
        # ensure fullscreen
        if path.exists(SONIC3AIR_SETTINGS_PATH):
            with open(SONIC3AIR_SETTINGS_PATH, 'r') as file:
                settings_data = load(file)
                settings_data["Fullscreen"] = 1
        else:
            settings_data = {"Fullscreen": 1}

        with open(SONIC3AIR_SETTINGS_PATH, 'w') as file:
            dump(settings_data, file, indent=4)

        # now run
        commandArray = [SONIC3AIR_BIN_PATH]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                    })

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
