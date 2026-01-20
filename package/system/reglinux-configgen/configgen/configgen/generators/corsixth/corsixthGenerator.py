from pathlib import Path

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

from .corsixthConfig import (
    CORSIXTH_BIN_PATH,
    CORSIXTH_CONFIG_DIR,
    CORSIXTH_CONFIG_PATH,
    CORSIXTH_GAME_DATA_DIR,
    CORSIXTH_SAVES_DIR,
    setCorsixthConfig,
)

eslog = get_logger(__name__)


class CorsixTHGenerator(Generator):
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
        # Create corsixth config directory if needed
        config_dir_path = Path(CORSIXTH_CONFIG_DIR)
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)

        # Create corsixth savesg directory if needed
        saves_dir_path = Path(CORSIXTH_SAVES_DIR)
        if not saves_dir_path.exists():
            saves_dir_path.mkdir(parents=True, exist_ok=True)

        # Check game data is installed
        try:
            for game_data in CORSIXTH_GAME_DATA_DIR:
                if not Path(game_data).exists():
                    raise FileNotFoundError(
                        f"ERROR: Game data ({game_data}) not found. You can get them from the game Theme Hospital.",
                    )
        except FileNotFoundError as e:
            eslog.exception(e)

        # If config file already exists, delete it
        config_path = Path(CORSIXTH_CONFIG_PATH)
        if config_path.exists():
            config_path.unlink()

        # Create the config file and fill it with basic data
        with Path(CORSIXTH_CONFIG_PATH).open("w") as corsixth_config_file:
            setCorsixthConfig(corsixth_config_file, system, game_resolution)

        # Launch engine with config file path
        command_array = [CORSIXTH_BIN_PATH, f"--config-file={CORSIXTH_CONFIG_PATH}"]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
