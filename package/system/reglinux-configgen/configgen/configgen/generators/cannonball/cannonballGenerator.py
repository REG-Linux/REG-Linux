from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs, linesep
from codecs import open
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from configgen.controllers import generate_sdl_controller_config
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

from .cannonballConfig import (
    CANNONBALL_BIN_PATH,
    CANNONBALL_CONFIG_PATH,
    setCannonballConfig,
)


class CannonballGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        if not path.exists(path.dirname(CANNONBALL_CONFIG_PATH)):
            makedirs(path.dirname(CANNONBALL_CONFIG_PATH))

        # config file
        cannoballConfig = minidom.Document()
        if path.exists(CANNONBALL_CONFIG_PATH):
            try:
                cannoballConfig = minidom.parse(CANNONBALL_CONFIG_PATH)
            except (ExpatError, FileNotFoundError, OSError) as e:
                eslog.debug(f"Cannonball: Failed to parse config file {CANNONBALL_CONFIG_PATH} - {str(e)}")
                pass  # reinit the file

        # cannonball config file
        setCannonballConfig(cannoballConfig, system)

        # save the config file
        cannonballXml = open(CANNONBALL_CONFIG_PATH, "w", "utf-8")
        dom_string = linesep.join(
            [s for s in cannoballConfig.toprettyxml().splitlines() if s.strip()]
        )  # remove ugly empty lines while minicom adds them...
        cannonballXml.write(dom_string)
        cannonballXml.close()

        # command line
        command_array = [CANNONBALL_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
