from os import listdir
from pathlib import Path

from configgen.Command import Command
from configgen.generators.Generator import Generator

try:
    from ruamel.yaml import YAML
except ImportError:
    print(
        "ruamel.yaml module not found. Please install it with: pip install ruamel.yaml",
    )
    raise
from shutil import move
from typing import Any

from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import CONF, SAVES

VITA3K_CONFIG_DIR = str(CONF / "vita3k")
VITA3K_SAVES_DIR = str(SAVES / "psvita")
VITA3K_CONFIG_PATH = str(CONF / "vita3k" / "config.yml")
VITA3K_BIN_PATH = "/usr/bin/vita3k/Vita3K"


class Vita3kGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

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
        # Create folder
        config_dir_path = Path(VITA3K_CONFIG_DIR)
        if not config_dir_path.is_dir():
            config_dir_path.mkdir(parents=True, exist_ok=True)
        saves_dir_path = Path(VITA3K_SAVES_DIR)
        if not saves_dir_path.is_dir():
            saves_dir_path.mkdir(parents=True, exist_ok=True)

        # Move saves if necessary
        ux0_path = config_dir_path / "ux0"
        if ux0_path.is_dir():
            # Move all folders from VITA3K_CONFIG_DIR to VITA3K_SAVES_DIR except "data", "lang", and "shaders-builtin"
            for item in listdir(VITA3K_CONFIG_DIR):
                if item not in ["data", "lang", "shaders-builtin"]:
                    item_path = config_dir_path / item
                    if item_path.is_dir():
                        move(str(item_path), VITA3K_SAVES_DIR)

        # Create the config.yml file if it doesn't exist
        vita3kymlconfig = {}
        indent = 2
        block_seq_indent = 0
        config_path = Path(VITA3K_CONFIG_PATH)
        if config_path.is_file():
            try:
                from ruamel.yaml.util import load_yaml_guess_indent

                with open(VITA3K_CONFIG_PATH) as stream:
                    vita3kymlconfig, indent, block_seq_indent = load_yaml_guess_indent(
                        stream,
                    )
            except ImportError:
                with open(VITA3K_CONFIG_PATH) as stream:
                    yaml = YAML()
                    vita3kymlconfig = yaml.load(stream)
                indent = 2
                block_seq_indent = 0

        if vita3kymlconfig is None:
            vita3kymlconfig = {}

        # ensure the correct path is set
        vita3kymlconfig["pref-path"] = VITA3K_SAVES_DIR

        # Set the renderer
        if system.isOptSet("vita3k_gfxbackend"):
            vita3kymlconfig["backend-renderer"] = system.config["vita3k_gfxbackend"]
        else:
            vita3kymlconfig["backend-renderer"] = "OpenGL"
        # Set the resolution multiplier
        if system.isOptSet("vita3k_resolution"):
            vita3kymlconfig["resolution-multiplier"] = int(
                system.config["vita3k_resolution"],
            )
        else:
            vita3kymlconfig["resolution-multiplier"] = 1
        # Set FXAA
        if system.isOptSet("vita3k_fxaa") and system.getOptBoolean("vita3k_surface"):
            vita3kymlconfig["enable-fxaa"] = "true"
        else:
            vita3kymlconfig["enable-fxaa"] = "false"
        # Set VSync
        if system.isOptSet("vita3k_vsync") and not system.getOptBoolean(
            "vita3k_surface",
        ):
            vita3kymlconfig["v-sync"] = "false"
        else:
            vita3kymlconfig["v-sync"] = "true"
        # Set the anisotropic filtering
        if system.isOptSet("vita3k_anisotropic"):
            vita3kymlconfig["anisotropic-filtering"] = int(
                system.config["vita3k_anisotropic"],
            )
        else:
            vita3kymlconfig["anisotropic-filtering"] = 1
        # Set the linear filtering option
        if system.isOptSet("vita3k_linear") and system.getOptBoolean("vita3k_surface"):
            vita3kymlconfig["enable-linear-filter"] = "true"
        else:
            vita3kymlconfig["enable-linear-filter"] = "false"
        # Surface Sync
        if system.isOptSet("vita3k_surface") and not system.getOptBoolean(
            "vita3k_surface",
        ):
            vita3kymlconfig["disable-surface-sync"] = "false"
        else:
            vita3kymlconfig["disable-surface-sync"] = "true"

        # Vita3k is fussy over its yml file
        # We try to match it as close as possible, but the 'vectors' cause yml formatting issues
        yaml = YAML()
        yaml.explicit_start = True
        yaml.explicit_end = True
        yaml.indent(mapping=indent, sequence=indent, offset=block_seq_indent)

        with open(VITA3K_CONFIG_PATH, "w") as fp:
            yaml.dump(vita3kymlconfig, fp)

        # Simplify the rom name (strip the directory & extension)
        begin, end = rom.find("["), rom.rfind("]")
        smplromname = rom[begin + 1 : end]
        # because of the yml formatting, we don't allow Vita3k to modify it
        # using the -w & -f options prevents Vita3k from re-writing & prompting the user in GUI
        # we want to avoid that so roms load straight away
        app_path = Path(VITA3K_SAVES_DIR) / "ux0" / "app" / smplromname
        if app_path.is_dir():
            command_array = [
                VITA3K_BIN_PATH,
                "-F",
                "-w",
                "-f",
                "-c",
                VITA3K_CONFIG_PATH,
                "-r",
                smplromname,
            ]
        else:
            # Game not installed yet, let's open the menu
            command_array = [
                VITA3K_BIN_PATH,
                "-F",
                "-w",
                "-f",
                "-c",
                VITA3K_CONFIG_PATH,
                rom,
            ]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )

    # Show mouse for touchscreen actions
    def getMouseMode(self, config, rom):
        return not (
            "vita3k_show_pointer" in config and config["vita3k_show_pointer"] == "0"
        )

    def get_in_game_ratio(
        self,
        config: Any,
        game_resolution: dict[str, int],
        rom: str,
    ) -> float:
        return 16 / 9
