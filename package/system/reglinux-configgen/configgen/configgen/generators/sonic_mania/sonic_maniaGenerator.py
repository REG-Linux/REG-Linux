from configparser import ConfigParser
from os import X_OK, access, chdir
from pathlib import Path
from shutil import copy
from stat import S_IRGRP, S_IROTH, S_IRWXU, S_IXGRP, S_IXOTH
from typing import Any

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import ROMS

SONICMANIA_SOURCE_BIN_PATH = Path("/usr/bin/sonic-mania")
SONICMANIA_ROMS_DIR = ROMS / "sonic-mania"
SONICAMANIA_BIN_PATH = SONICMANIA_ROMS_DIR / "sonic-mania"
SONICMANIA_CONFIG_PATH = SONICMANIA_ROMS_DIR / "Settings.ini"


class SonicManiaGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        # Create the roms directory if it doesn't exist
        SONICMANIA_ROMS_DIR.mkdir(parents=True, exist_ok=True)

        # Check if source binary exists and is executable
        if not SONICMANIA_SOURCE_BIN_PATH.exists():
            raise FileNotFoundError(
                f"Source binary not found: {SONICMANIA_SOURCE_BIN_PATH}",
            )

        if not access(str(SONICMANIA_SOURCE_BIN_PATH), X_OK):
            raise PermissionError(
                f"Source binary is not executable: {SONICMANIA_SOURCE_BIN_PATH}",
            )

        # Copy the binary if it doesn't exist or is different
        copy_needed = True
        if SONICAMANIA_BIN_PATH.exists():
            # Check if files are different
            import filecmp

            if filecmp.cmp(
                str(SONICMANIA_SOURCE_BIN_PATH),
                str(SONICAMANIA_BIN_PATH),
                shallow=False,
            ):
                copy_needed = False

        if copy_needed:
            copy(str(SONICMANIA_SOURCE_BIN_PATH), str(SONICAMANIA_BIN_PATH))
            # Make sure the copied binary is executable
            if not SONICAMANIA_BIN_PATH.exists() or not access(
                str(SONICAMANIA_BIN_PATH), X_OK,
            ):
                import os

                os.chmod(
                    str(SONICAMANIA_BIN_PATH),
                    S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH,
                )

        # Verify the copied binary is executable
        if not access(str(SONICAMANIA_BIN_PATH), X_OK):
            raise PermissionError(
                f"Copied binary is not executable: {SONICAMANIA_BIN_PATH}",
            )

        ## Configuration

        # VSync
        if system.isOptSet("smania_vsync"):
            selected_vsync = system.config["smania_vsync"]
        else:
            selected_vsync = "y"
        # Triple Buffering
        if system.isOptSet("smania_buffering"):
            selected_buffering = system.config["smania_buffering"]
        else:
            selected_buffering = "n"
        # Language
        if system.isOptSet("smania_language"):
            selected_language = system.config["smania_language"]
        else:
            selected_language = "0"

        ## Create the Settings.ini file
        config = ConfigParser()
        config.optionxform = lambda optionstr: str(optionstr)
        # Game
        config["Game"] = {
            "devMenu": "y",
            "faceButtonFlip": "n",
            "enableControllerDebugging": "n",
            "disableFocusPause": "n",
            "region": "-1",
            "language": selected_language,
        }
        # Video
        config["Video"] = {
            "windowed": "n",
            "border": "n",
            "exclusiveFS": "y",
            "vsync": selected_vsync,
            "tripleBuffering": selected_buffering,
            "winWidth": str(game_resolution["width"]),
            "winHeight": str(game_resolution["height"]),
            "refreshRate": "60",
            "shaderSupport": "y",
            "screenShader": "1",
            "maxPixWidth": "0",
        }
        # Audio
        config["Audio"] = {
            "streamsEnabled": "y",
            "streamVolume": "1.000000",
            "sfxVolume": "1.000000",
        }
        # Save the ini file
        with open(SONICMANIA_CONFIG_PATH, "w") as configfile:
            config.write(configfile)

        # Now run
        chdir(str(SONICMANIA_ROMS_DIR))
        command_array = [str(SONICAMANIA_BIN_PATH)]

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
        return False

    def get_in_game_ratio(
        self, config: Any, game_resolution: dict[str, int], rom: str,
    ) -> float:
        return 16 / 9
