from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs, symlink
from shutil import copyfile
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import CONF, SCREENSHOTS

SDLPOP_CONFIG_DIR = CONF + "/SDLPoP"
SDLPOP_SCREENSHOTS_DIR = SCREENSHOTS + "/SDLPoP"
SDLPOP_SOURCE_CFG_PATH = SDLPOP_CONFIG_DIR + "/SDLPoP.cfg"
SDLPOP_SOURCE_INI_PATH = SDLPOP_CONFIG_DIR + "/SDLPoP.ini"
SDLPOP_DEST_CFG_PATH = "/usr/share/SDLPoP/cfg/SDLPoP.cfg"
SDLPOP_DEST_INI_PATH = "/usr/share/SDLPoP/cfg/SDLPoP.ini"
SDLPOP_SOURCE_SCREENSHOTS_DIR = "/usr/share/SDLPoP/screenshots"


class SdlPopGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = ["SDLPoP"]

        # create sdlpop config directory
        if not path.exists(SDLPOP_CONFIG_DIR):
            makedirs(SDLPOP_CONFIG_DIR)
        if not path.exists(SDLPOP_SOURCE_CFG_PATH):
            copyfile(SDLPOP_DEST_CFG_PATH, SDLPOP_SOURCE_CFG_PATH)
        if not path.exists(SDLPOP_SOURCE_INI_PATH):
            copyfile(SDLPOP_DEST_INI_PATH, SDLPOP_SOURCE_INI_PATH)
        # symbolic link cfg files
        if not path.exists(SDLPOP_DEST_CFG_PATH):
            symlink(SDLPOP_SOURCE_CFG_PATH, SDLPOP_DEST_CFG_PATH)
        if not path.exists(SDLPOP_DEST_INI_PATH):
            symlink(SDLPOP_SOURCE_INI_PATH, SDLPOP_DEST_INI_PATH)
        # create screenshots folder in /userdata
        if not path.exists(SDLPOP_SCREENSHOTS_DIR):
            makedirs(SDLPOP_SCREENSHOTS_DIR)
        # symbolic link screenshot folder too
        if not path.exists(SDLPOP_SOURCE_SCREENSHOTS_DIR):
            symlink(
                SDLPOP_SCREENSHOTS_DIR,
                SDLPOP_SOURCE_SCREENSHOTS_DIR,
                target_is_directory=True,
            )

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
