from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs
from configgen.settings import JSONSettings
from configgen.controllers import generate_sdl_controller_config
from .bigpemuConfig import (
    setBigemuConfig,
    BIGPEMU_BIN_PATH,
    BIGPEMU_CONFIG_DIR,
    BIGPEMU_CONFIG_PATH,
)


class BigPEmuGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Create the directory if it doesn't exist
        if not path.exists(BIGPEMU_CONFIG_DIR):
            makedirs(BIGPEMU_CONFIG_DIR)

        # Load existing configuration or create a new one
        bigpemuConfig = JSONSettings(BIGPEMU_CONFIG_PATH)

        # Update configuration
        setBigemuConfig(bigpemuConfig, system, gameResolution, playersControllers)

        # Save the updated configuration
        bigpemuConfig.write()

        commandArray = [BIGPEMU_BIN_PATH, rom]
        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
