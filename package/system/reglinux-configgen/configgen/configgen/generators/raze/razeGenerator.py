from os import mkdir, path
from platform import uname

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF, SAVES
from configgen.utils.buildargs import parse_args
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

RAZE_CONFIG_DIR = CONF + "/raze"
RAZE_SAVES_DIR = SAVES + "/raze"
RAZE_CONFIG_FILE = RAZE_CONFIG_DIR + "/raze.ini"
RAZE_SCRIPT_FILE = RAZE_CONFIG_DIR + "/raze.cfg"


class RazeGenerator(Generator):
    # Names that Raze uses for game series specific sections in the config file
    game_names = [
        "Blood",
        "Duke",
        "Exhumed",
        "Nam",
        "Redneck",
        "ShadowWarrior",
        "WW2GI",
    ]
    # Options for config file that has more sensible controls and defaults, but only on first boot so overrides persist
    # Raze does not support global bindings; set defaults for each game series
    config_defaults = {}
    for name in game_names:
        config_defaults[f"{name}.ConsoleVariables"] = {
            "hud_size": 8,  # fullscreen / minimal HUD
            "m_sensitivity_x": 6.0,  # speed up movement and look slightly; its a bit slow as default
            "m_sensitivity_y": 5.5,
        }
        # ESC cannot be rebound, which is fine, we override in raze.keys
        config_defaults[f"{name}.Bindings"] = {
            "F6": "quicksave",  # F-keys accessed via raze.keys bindings
            "F9": "quickload",
            "F12": "screenshot",
            "C": "toggleconsole",  # useful for debugging and testing
            "Tab": "togglemap",
            "E": "+Move_Forward",
            "D": "+Move_Backward",
            "S": "+Strafe_Left",
            "F": "+Strafe_Right",
            "PgUp": "+Quick_Kick",  # used in several games
            "PgDn": "+Alt_Fire",  # used in Blood
            "End": "+Crouch",
            "Home": "+Fire",
            "Del": "toggle cl_autorun",
            "Ins": "+toggle_crouch",
            "UpArrow": "weapprev",
            "DownArrow": "weapnext",
            "LeftArrow": "invprev",
            "RightArrow": "invnext",
            "X": "invuse",
            "B": "+jump",
            "Y": "+open",
            "A": "+open",
        }
        config_defaults[f"{name}.AutomapBindings"] = {
            "PgUp": "+Shrink_Screen",
            "PgDn": "+Enlarge_Screen",
            "UpArrow": "+am_panup",
            "DownArrow": "+am_pandown",
            "LeftArrow": "+am_panleft",
            "RightArrow": "+am_panright",
            "Del": "togglefollow",
            "Ins": "togglerotate",
        }

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Remove unused arguments: metadata, guns, wheels
        architecture = get_cpu_architecture()
        eslog.debug(f"*** Detected architecture is: {architecture} ***")

        for dir in [RAZE_CONFIG_DIR, RAZE_SAVES_DIR]:
            if not path.exists(dir):
                mkdir(dir)

        if not path.exists(RAZE_CONFIG_FILE):
            with open(RAZE_CONFIG_FILE, "w") as config:
                for section in self.config_defaults:
                    config.write(f"[{section}]\n")
                    for key, value in self.config_defaults[section].items():
                        config.write(f"{key}={value}\n")
                    config.write("\n")

        config_backup = []
        if path.exists(RAZE_CONFIG_FILE):
            with open(RAZE_CONFIG_FILE) as original_file:
                config_backup = original_file.readlines()

        with open(RAZE_CONFIG_FILE, "w") as config_file:
            global_settings_found = False
            for line in config_backup:
                # Check for the [GlobalSettings] section
                if line.strip() == "[GlobalSettings]":
                    global_settings_found = True

                # Modify options in the [GlobalSettings] section
                if global_settings_found:
                    # always set gl_es to true for arm
                    if line.strip().startswith("gl_es="):
                        if (
                            system.isOptSet("raze_api")
                            and system.config["raze_api"] != "2"
                        ):
                            if (
                                system.isOptSet("raze_api")
                                and system.config["raze_api"] == "0"
                            ):
                                if architecture in ["x86_64", "amd64"]:
                                    line = "gl_es=false\n"
                                else:
                                    eslog.debug(
                                        f"*** Architecture isn't intel it's: {architecture} therefore es is true ***"
                                    )
                                    line = "gl_es=true\n"
                        else:
                            line = "gl_es=true\n"
                    elif line.strip().startswith("vid_preferbackend="):
                        if system.isOptSet("raze_api"):
                            line = f"vid_preferbackend={system.config['raze_api']}\n"
                        else:
                            line = "vid_preferbackend=2\n"

                # Write the line
                config_file.write(line)

            # If [GlobalSettings] was not found, add it with the modified options
            if not global_settings_found:
                eslog.debug("Global Settings NOT found")
                config_file.write("[GlobalSettings]\n")
                if system.isOptSet("raze_api") and system.config["raze_api"] != "2":
                    if system.isOptSet("raze_api") and system.config["raze_api"] == "0":
                        if architecture in ["x86_64", "amd64"]:
                            config_file.write("gl_es=false\n")
                        else:
                            eslog.debug(
                                f"*** Architecture isn't intel it's: {architecture} therefore es is true ***"
                            )
                            config_file.write("gl_es=true\n")
                if system.isOptSet("raze_api"):
                    config_file.write(
                        f"vid_preferbackend={system.config['raze_api']}\n"
                    )
                else:
                    config_file.write("vid_preferbackend=2\n")

        with open(RAZE_SCRIPT_FILE, "w") as script:
            script.write(
                "# This file is automatically generated by razeGenerator.py\n"
                f"vid_fps {'true' if system.getOptBoolean('showFPS') else 'false'}\n"
                "echo REG-Linux\n"  # easy check that script ran in console
            )

        # Launch arguments
        command_array = ["raze"]
        result = parse_args(command_array, rom)
        if not result.okay:
            raise Exception(result.message)

        command_array += [
            "-exec",
            RAZE_SCRIPT_FILE,
            # Disable controllers because support is poor; we use evmapy instead
            "-nojoy",
            "-width",
            str(game_resolution["width"]),
            "-height",
            str(game_resolution["height"]),
            "-nologo" if system.getOptBoolean("nologo") else "",
        ]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )

    def get_in_game_ratio(self, config, game_resolution, rom):
        return 16 / 9


def get_cpu_architecture():
    return uname().machine
