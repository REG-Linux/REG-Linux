from generators.Generator import Generator
from Command import Command
from os import path, makedirs
from shutil import copy
from systemFiles import CONF
from settings import UnixSettings
from controllers import generate_sdl_controller_config
from .moonlightConfig import (
    setMoonlightConfig,
    MOONLIGHT_BIN_PATH,
    MOONLIGHT_GAMELIST_PATH,
    MOONLIGHT_STAGING_CONFIG_PATH,
    MOONLIGHT_CONFIG_DIR,
    MOONLIGHT_CONFIG_PATH,
)


class MoonlightGenerator(Generator):
    def getResolutionMode(self, config):
        return "default"

    # Main entry of the module
    # Configure fba and return a command
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        if not path.exists(MOONLIGHT_CONFIG_DIR + "/staging"):
            makedirs(MOONLIGHT_CONFIG_DIR + "/staging")

        # If user made config file exists, copy to staging directory for use
        if path.exists(MOONLIGHT_CONFIG_PATH):
            copy(MOONLIGHT_CONFIG_PATH, MOONLIGHT_STAGING_CONFIG_PATH)

        # Load the config file
        moonlightConfig = UnixSettings(MOONLIGHT_STAGING_CONFIG_PATH, separator=" ")

        # Set the config options
        setMoonlightConfig(moonlightConfig, system)

        # Save the config file
        moonlightConfig.write()

        gameName, confFile = self.getRealGameNameAndConfigFile(rom)
        commandArray = [MOONLIGHT_BIN_PATH, "stream", "-config", confFile]
        commandArray.append("-app")
        commandArray.append(gameName)
        commandArray.append("-debug")

        return Command(
            array=commandArray,
            env={
                "XDG_DATA_DIRS": CONF,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                ),
            },
        )

    def getRealGameNameAndConfigFile(self, rom):
        # Rom's basename without extension
        romName = path.splitext(path.basename(rom))[0]
        # find the real game name
        try:
            with open(MOONLIGHT_GAMELIST_PATH, "r") as f:
                gfeGame = None
                for line in f:
                    try:
                        gfeRom, gfeGame, confFile = line.rstrip().split(";")
                        # confFile = confFile.rstrip()
                    except ValueError:  # When there are not enough values to unpack
                        gfeRom, gfeGame = line.rstrip().split(";")
                        confFile = MOONLIGHT_STAGING_CONFIG_PATH
                    # If found
                    if gfeRom == romName:
                        # return it
                        return [gfeGame, confFile]
                # If nothing is found (old gamelist file format ?)
                return [gfeGame, MOONLIGHT_STAGING_CONFIG_PATH]
        except FileNotFoundError:
            eslog.error(f"Moonlight gamelist file not found: {MOONLIGHT_GAMELIST_PATH}")
            return [None, MOONLIGHT_STAGING_CONFIG_PATH]
        except PermissionError:
            eslog.error(f"Permission denied accessing Moonlight gamelist file: {MOONLIGHT_GAMELIST_PATH}")
            return [None, MOONLIGHT_STAGING_CONFIG_PATH]
        except Exception as e:
            eslog.error(f"Error reading Moonlight gamelist file {MOONLIGHT_GAMELIST_PATH}: {e}")
            return [None, MOONLIGHT_STAGING_CONFIG_PATH]
