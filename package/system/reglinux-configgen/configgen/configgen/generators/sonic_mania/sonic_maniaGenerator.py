from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, chdir, access, X_OK
from shutil import copy
from configparser import ConfigParser
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import ROMS
from stat import S_IRWXU, S_IRGRP, S_IXGRP, S_IROTH, S_IXOTH

SONICMANIA_SOURCE_BIN_PATH = "/usr/bin/sonic-mania"
SONICMANIA_ROMS_DIR = ROMS + "/sonic-mania"
SONICAMANIA_BIN_PATH = SONICMANIA_ROMS_DIR + "/sonic-mania"
SONICMANIA_CONFIG_PATH = SONICMANIA_ROMS_DIR + "/Settings.ini"


class SonicManiaGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Create the roms directory if it doesn't exist
        if not path.exists(SONICMANIA_ROMS_DIR):
            import os

            os.makedirs(SONICMANIA_ROMS_DIR, exist_ok=True)

        # Check if source binary exists and is executable
        if not path.exists(SONICMANIA_SOURCE_BIN_PATH):
            raise FileNotFoundError(
                f"Source binary not found: {SONICMANIA_SOURCE_BIN_PATH}"
            )

        if not access(SONICMANIA_SOURCE_BIN_PATH, X_OK):
            raise PermissionError(
                f"Source binary is not executable: {SONICMANIA_SOURCE_BIN_PATH}"
            )

        # Copy the binary if it doesn't exist or is different
        copy_needed = True
        if path.exists(SONICAMANIA_BIN_PATH):
            # Check if files are different
            import filecmp

            if filecmp.cmp(
                SONICMANIA_SOURCE_BIN_PATH, SONICAMANIA_BIN_PATH, shallow=False
            ):
                copy_needed = False

        if copy_needed:
            copy(SONICMANIA_SOURCE_BIN_PATH, SONICAMANIA_BIN_PATH)
            # Make sure the copied binary is executable
            if not path.exists(SONICAMANIA_BIN_PATH) or not access(
                SONICAMANIA_BIN_PATH, X_OK
            ):
                import os

                os.chmod(
                    SONICAMANIA_BIN_PATH,
                    S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH,
                )

        # Verify the copied binary is executable
        if not access(SONICAMANIA_BIN_PATH, X_OK):
            raise PermissionError(
                f"Copied binary is not executable: {SONICAMANIA_BIN_PATH}"
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
            "winWidth": str(gameResolution["width"]),
            "winHeight": str(gameResolution["height"]),
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
        chdir(SONICMANIA_ROMS_DIR)
        commandArray = [SONICAMANIA_BIN_PATH]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
