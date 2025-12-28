from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

from .viceConfig import VICE_BIN_DIR, setViceConfig
from .viceControllers import setViceControllers

eslog = get_logger(__name__)


class ViceGenerator(Generator):
    def getResolutionMode(self, config):
        return "default"

    # Main entry of the module
    # Return command
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        setViceConfig(system, metadata, guns)
        setViceControllers(system, players_controllers)

        command_array = [VICE_BIN_DIR + system.config["core"], rom]
        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
