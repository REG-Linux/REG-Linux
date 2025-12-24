from configparser import ConfigParser, DuplicateOptionError
from os import makedirs, path, rename
from shutil import copy

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger
from configgen.utils.systemServices import get_service_status

from . import vpinballWindowing
from .vpinballConfig import (
    VPINBALL_ASSETS_PATH,
    VPINBALL_BIN_PATH,
    VPINBALL_CONFIG_DIR,
    VPINBALL_CONFIG_PATH,
    VPINBALL_LOG_PATH,
    VPINBALL_PINMAME_PATH,
    setVpinballConfig,
)

eslog = get_logger(__name__)


class VPinballGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # create vpinball config directory and default config file if they don't exist
        if not path.exists(VPINBALL_CONFIG_DIR):
            makedirs(VPINBALL_CONFIG_DIR)
        if not path.exists(VPINBALL_CONFIG_PATH):
            copy(VPINBALL_ASSETS_PATH, VPINBALL_CONFIG_PATH)
        if not path.exists(VPINBALL_PINMAME_PATH):
            makedirs(VPINBALL_PINMAME_PATH)
        if path.exists(VPINBALL_LOG_PATH):
            rename(VPINBALL_LOG_PATH, VPINBALL_LOG_PATH + ".1")

        ## [ VPinballX.ini ] ##
        try:
            vpinballSettings = ConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.optionxform = lambda optionstr: str(optionstr)
            vpinballSettings.read(VPINBALL_CONFIG_PATH)
        except DuplicateOptionError as e:
            eslog.debug(f"Error reading VPinballX.ini: {e}")
            eslog.debug("*** Using default VPinballX.ini file ***")
            copy(VPINBALL_ASSETS_PATH, VPINBALL_CONFIG_PATH)
            vpinballSettings = ConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.optionxform = lambda optionstr: str(optionstr)
            vpinballSettings.read(VPINBALL_CONFIG_PATH)

        # init sections
        if not vpinballSettings.has_section("Standalone"):
            vpinballSettings.add_section("Standalone")
        if not vpinballSettings.has_section("Player"):
            vpinballSettings.add_section("Player")
        if not vpinballSettings.has_section("TableOverride"):
            vpinballSettings.add_section("TableOverride")

        # options
        setVpinballConfig(vpinballSettings, system)

        # dmd
        hasDmd = get_service_status("dmd_real") == "started"

        # windows
        vpinballWindowing.configureWindowing(
            vpinballSettings, system, game_resolution, hasDmd
        )

        # DMDServer
        if hasDmd:
            vpinballSettings.set("Standalone", "DMDServer", "1")
        else:
            vpinballSettings.set("Standalone", "DMDServer", "0")

        # Save VPinballX.ini
        with open(VPINBALL_CONFIG_PATH, "w") as configfile:
            vpinballSettings.write(configfile)

        # set the config path to be sure
        command_array = [
            VPINBALL_BIN_PATH,
            "-PrefPath",
            VPINBALL_CONFIG_DIR,
            "-Ini",
            VPINBALL_CONFIG_PATH,
            "-Play",
            rom,
        ]

        # SDL_RENDER_VSYNC is causing perf issues (set by emulatorlauncher.py)
        return Command(
            array=command_array,
            env={
                "SDL_RENDER_VSYNC": "0",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                ),
            },
        )

    def get_in_game_ratio(self, config, game_resolution, rom):
        return 16 / 9
