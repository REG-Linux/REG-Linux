from pathlib import Path
from shutil import copy
from typing import Any

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator
from configgen.systemFiles import CONF


class ETLegacyGenerator(Generator):
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
        etLegacyDir = "/userdata/roms/etlegacy/legacy"
        etLegacyFile = "/legacy_2.83-dirty.pk3"
        etLegacySource = str(Path("/usr/share/etlegacy") / etLegacyFile.lstrip("/"))
        etLegacyDest = str(Path(etLegacyDir) / etLegacyFile.lstrip("/"))

        # Configuration

        # Config file path
        config_dir = str(Path(CONF) / "etlegacy" / "legacy")
        config_file_path = str(Path(config_dir) / "etconfig.cfg")

        config_dir_path = Path(config_dir)
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)

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
        if Path(config_file_path).is_file():
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
        et_legacy_dir_path = Path(etLegacyDir)
        if not et_legacy_dir_path.exists():
            et_legacy_dir_path.mkdir(parents=True, exist_ok=True)

        # copy latest mod file to the rom directory
        et_legacy_dest_path = Path(etLegacyDest)
        if not et_legacy_dest_path.exists():
            copy(etLegacySource, etLegacyDest)
        else:
            source_version = Path(etLegacySource).stat().st_mtime
            destination_version = et_legacy_dest_path.stat().st_mtime
            if source_version > destination_version:
                copy(etLegacySource, etLegacyDest)

        command_array = ["etl"]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def get_in_game_ratio(
        self,
        config: Any,
        game_resolution: dict[str, int],
        rom: str,
    ) -> float:
        return 16 / 9
