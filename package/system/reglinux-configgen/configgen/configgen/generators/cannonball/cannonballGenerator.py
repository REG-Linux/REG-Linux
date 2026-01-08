from codecs import open as codecs_open
from os import linesep
from pathlib import Path
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

from .cannonballConfig import (
    CANNONBALL_BIN_PATH,
    CANNONBALL_CONFIG_PATH,
    setCannonballConfig,
)

eslog = get_logger(__name__)


class CannonballGenerator(Generator):
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
        config_dir_path = Path(CANNONBALL_CONFIG_PATH).parent
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)

        # config file
        cannoballConfig = minidom.Document()
        config_path = Path(CANNONBALL_CONFIG_PATH)
        if config_path.exists():
            try:
                cannoballConfig = minidom.parse(CANNONBALL_CONFIG_PATH)
            except (ExpatError, FileNotFoundError, OSError) as e:
                eslog.debug(
                    f"Cannonball: Failed to parse config file {CANNONBALL_CONFIG_PATH} - {e!s}",
                )
                # reinit the file

        # cannonball config file
        setCannonballConfig(cannoballConfig, system)

        # save the config file
        with codecs_open(
            CANNONBALL_CONFIG_PATH, "w", encoding="utf-8"
        ) as cannonballXml:
            dom_string = linesep.join(
                [s for s in cannoballConfig.toprettyxml().splitlines() if s.strip()],
            )  # remove ugly empty lines while minicom adds them...
            cannonballXml.write(dom_string)
            cannonballXml.close()

        # command line
        command_array = [CANNONBALL_BIN_PATH]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
