from os import makedirs, path
from shutil import copy
from typing import Any

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF


class ETLegacyGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        etLegacyDir = "/userdata/roms/etlegacy/legacy"
        etLegacyFile = "/legacy_2.83-dirty.pk3"
        etLegacySource = "/usr/share/etlegacy" + etLegacyFile
        etLegacyDest = etLegacyDir + etLegacyFile

        ## Configuration

        # Config file path
        config_dir = CONF + "/etlegacy/legacy"
        config_file_path = config_dir + "/etconfig.cfg"

        if not path.exists(config_dir):
            makedirs(config_dir)

        # Define the options to add or modify
        options_to_set = {
            "seta r_mode": "-1",
            "seta r_fullscreen": "1",
            "seta r_allowResize": "0",
            "seta r_centerWindow": "1",
            "seta r_customheight": f'"{game_resolution["height"]}"',
            "seta r_customwidth": f'"{game_resolution["width"]}"',
        }

        # Set language
        if system.isOptSet("etlegacy_language"):
            options_to_set["seta cl_lang"] = system.config["etlegacy_language"]
            options_to_set["seta ui_cl_lang"] = system.config["etlegacy_language"]
        else:
            options_to_set["seta cl_lang"] = "en"
            options_to_set["seta ui_cl_lang"] = "en"

        # Check if the file exists
        if path.isfile(config_file_path):
            with open(config_file_path) as config_file:
                lines = config_file.readlines()

            # Loop through the options and update the lines
            for key, value in options_to_set.items():
                option_exists = any(key in line for line in lines)
                if not option_exists:
                    lines.append(f'{key} "{value}"\n')
                else:
                    for i, line in enumerate(lines):
                        if key in line:
                            lines[i] = f'{key} "{value}"\n'

            # Write the modified content back to the file
            with open(config_file_path, "w") as config_file:
                config_file.writelines(lines)
        else:
            # File doesn't exist, create it and add the options
            with open(config_file_path, "w") as config_file:
                for key, value in options_to_set.items():
                    config_file.write(f'{key} "{value}"\n')

        # copy mod files needed
        if not path.exists(etLegacyDir):
            makedirs(etLegacyDir)

        # copy latest mod file to the rom directory
        if not path.exists(etLegacyDest):
            copy(etLegacySource, etLegacyDest)
        else:
            source_version = path.getmtime(etLegacySource)
            destination_version = path.getmtime(etLegacyDest)
            if source_version > destination_version:
                copy(etLegacySource, etLegacyDest)

        command_array = ["etl"]

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
        return True

    def get_in_game_ratio(
        self, config: Any, game_resolution: dict[str, int], rom: str
    ) -> float:
        return 16 / 9
