from pathlib import Path
from shutil import copyfile

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF, SCREENSHOTS

SDLPOP_CONFIG_DIR = str(CONF / "SDLPoP")
SDLPOP_SCREENSHOTS_DIR = str(SCREENSHOTS / "SDLPoP")
SDLPOP_SOURCE_CFG_PATH = str(CONF / "SDLPoP" / "SDLPoP.cfg")
SDLPOP_SOURCE_INI_PATH = str(CONF / "SDLPoP" / "SDLPoP.ini")
SDLPOP_DEST_CFG_PATH = "/usr/share/SDLPoP/cfg/SDLPoP.cfg"
SDLPOP_DEST_INI_PATH = "/usr/share/SDLPoP/cfg/SDLPoP.ini"
SDLPOP_SOURCE_SCREENSHOTS_DIR = "/usr/share/SDLPoP/screenshots"


class SdlPopGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        command_array = ["SDLPoP"]

        # create sdlpop config directory
        config_dir_path = Path(SDLPOP_CONFIG_DIR)
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)
        source_cfg_path = Path(SDLPOP_SOURCE_CFG_PATH)
        if not source_cfg_path.exists():
            copyfile(SDLPOP_DEST_CFG_PATH, SDLPOP_SOURCE_CFG_PATH)
        source_ini_path = Path(SDLPOP_SOURCE_INI_PATH)
        if not source_ini_path.exists():
            copyfile(SDLPOP_DEST_INI_PATH, SDLPOP_SOURCE_INI_PATH)
        # symbolic link cfg files
        dest_cfg_path = Path(SDLPOP_DEST_CFG_PATH)
        if not dest_cfg_path.exists():
            dest_cfg_path.symlink_to(Path(SDLPOP_SOURCE_CFG_PATH))
        dest_ini_path = Path(SDLPOP_DEST_INI_PATH)
        if not dest_ini_path.exists():
            dest_ini_path.symlink_to(Path(SDLPOP_SOURCE_INI_PATH))
        # create screenshots folder in /userdata
        screenshots_dir_path = Path(SDLPOP_SCREENSHOTS_DIR)
        if not screenshots_dir_path.exists():
            screenshots_dir_path.mkdir(parents=True, exist_ok=True)
        # symbolic link screenshot folder too
        source_screenshots_path = Path(SDLPOP_SOURCE_SCREENSHOTS_DIR)
        if not source_screenshots_path.exists():
            source_screenshots_path.symlink_to(
                Path(SDLPOP_SCREENSHOTS_DIR),
                target_is_directory=True,
            )

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
