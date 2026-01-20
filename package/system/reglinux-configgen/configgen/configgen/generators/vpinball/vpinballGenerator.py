from configparser import ConfigParser, DuplicateOptionError
from os import rename
from pathlib import Path
from shutil import copy
from typing import Any

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator
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
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    ):
        # create vpinball config directory and default config file if they don't exist
        config_dir_path = Path(VPINBALL_CONFIG_DIR)
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)
        config_path = Path(VPINBALL_CONFIG_PATH)
        if not config_path.exists():
            copy(VPINBALL_ASSETS_PATH, VPINBALL_CONFIG_PATH)
        pinmame_path = Path(VPINBALL_PINMAME_PATH)
        if not pinmame_path.exists():
            pinmame_path.mkdir(parents=True, exist_ok=True)
        log_path = Path(VPINBALL_LOG_PATH)
        if log_path.exists():
            rename(VPINBALL_LOG_PATH, VPINBALL_LOG_PATH + ".1")

        # [ VPinballX.ini ] ##
        try:
            vpinballSettings = ConfigParser(interpolation=None, allow_no_value=True)

            def preserve_case(optionstr):
                return str(optionstr)

            vpinballSettings.optionxform = preserve_case
            vpinballSettings.read(VPINBALL_CONFIG_PATH)
        except DuplicateOptionError as e:
            eslog.debug(f"Error reading VPinballX.ini: {e}")
            eslog.debug("*** Using default VPinballX.ini file ***")
            copy(VPINBALL_ASSETS_PATH, VPINBALL_CONFIG_PATH)
            vpinballSettings = ConfigParser(interpolation=None, allow_no_value=True)

            def preserve_case(optionstr):
                return str(optionstr)

            vpinballSettings.optionxform = preserve_case
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
            vpinballSettings,
            system,
            game_resolution,
            hasDmd,
        )

        # DMDServer
        if hasDmd:
            vpinballSettings.set("Standalone", "DMDServer", "1")
        else:
            vpinballSettings.set("Standalone", "DMDServer", "0")

        # Save VPinballX.ini
        with open(VPINBALL_CONFIG_PATH, "w", encoding="utf-8") as configfile:
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
                    players_controllers,
                ),
            },
        )

    def get_in_game_ratio(
        self,
        config: Any,
        game_resolution: dict[str, int],
        rom: str,
    ) -> float:
        return 16 / 9
