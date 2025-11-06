from generators.Generator import Generator
from Command import Command
from controllers import generate_sdl_controller_config
from .viceConfig import setViceConfig, VICE_BIN_DIR
from .viceControllers import setViceControllers
from utils.logger import get_logger

eslog = get_logger(__name__)


class ViceGenerator(Generator):
    def getResolutionMode(self, config):
        return "default"

    # Main entry of the module
    # Return command
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        setViceConfig(system, metadata, guns)
        setViceControllers(system, playersControllers)

        commandArray = [VICE_BIN_DIR + system.config["core"], rom]
        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
