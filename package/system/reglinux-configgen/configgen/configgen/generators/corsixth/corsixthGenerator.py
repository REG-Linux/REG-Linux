from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs, unlink
from configgen.controllers import generate_sdl_controller_config
from .corsixthConfig import (
    CORSIXTH_CONFIG_DIR,
    CORSIXTH_SAVES_DIR,
    CORSIXTH_CONFIG_PATH,
    CORSIXTH_BIN_PATH,
    CORSIXTH_GAME_DATA_DIR,
    setCorsixthConfig,
)

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class CorsixTHGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Create corsixth config directory if needed
        if not path.exists(CORSIXTH_CONFIG_DIR):
            makedirs(CORSIXTH_CONFIG_DIR)

        # Create corsixth savesg directory if needed
        if not path.exists(CORSIXTH_SAVES_DIR):
            makedirs(CORSIXTH_SAVES_DIR)

        # Check game data is installed
        try:
            for game_data in CORSIXTH_GAME_DATA_DIR:
                if not path.exists(game_data):
                    raise FileNotFoundError(
                        f"ERROR: Game data ({game_data}) not found. You can get them from the game Theme Hospital."
                    )
        except FileNotFoundError as e:
            eslog.exception(e)

        # If config file already exists, delete it
        if path.exists(CORSIXTH_CONFIG_PATH):
            unlink(CORSIXTH_CONFIG_PATH)

        # Create the config file and fill it with basic data
        corsixth_config_file = open(CORSIXTH_CONFIG_PATH, "w")

        setCorsixthConfig(corsixth_config_file, system, game_resolution)

        # Close config file as we are done
        corsixth_config_file.close()

        # Launch engine with config file path
        command_array = [CORSIXTH_BIN_PATH, "--config-file=" + CORSIXTH_CONFIG_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
