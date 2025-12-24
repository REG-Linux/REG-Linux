from os import makedirs, path
from shutil import copy

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.settings import UnixSettings
from configgen.systemFiles import CONF
from configgen.utils.logger import get_logger

from .moonlightConfig import (
    MOONLIGHT_BIN_PATH,
    MOONLIGHT_CONFIG_DIR,
    MOONLIGHT_CONFIG_PATH,
    MOONLIGHT_GAMELIST_PATH,
    MOONLIGHT_STAGING_CONFIG_PATH,
    setMoonlightConfig,
)

eslog = get_logger(__name__)


class MoonlightGenerator(Generator):
    def getResolutionMode(self, config):
        return "default"

    # Main entry of the module
    # Configure fba and return a command
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
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

        game_name, confFile = self.getRealGameNameAndConfigFile(rom)
        command_array = [MOONLIGHT_BIN_PATH, "stream", "-config", confFile]
        command_array.append("-app")
        command_array.append(game_name)
        command_array.append("-debug")

        return Command(
            array=command_array,
            env={
                "XDG_DATA_DIRS": CONF,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                ),
            },
        )

    def getRealGameNameAndConfigFile(self, rom):
        # Rom's basename without extension
        romName = path.splitext(path.basename(rom))[0]
        # find the real game name
        try:
            with open(MOONLIGHT_GAMELIST_PATH) as f:
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
