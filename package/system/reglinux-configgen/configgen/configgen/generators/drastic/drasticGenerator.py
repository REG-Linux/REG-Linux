from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, chdir
from shutil import copytree
from configgen.controllers import generate_sdl_controller_config
from .drasticControllers import setDrasticController
from .drasticConfig import (
    DRASTIC_CONFIG_DIR,
    DRASTIC_CONFIG_DIR_USER,
    DRASTIC_CONFIG_PATH,
    DRASTIC_BIN_PATH,
    setDrasticConfig,
)


class DrasticGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Create the config directory if it doesn't exist
        if not path.exists(DRASTIC_CONFIG_DIR_USER):
            copytree(DRASTIC_CONFIG_DIR, DRASTIC_CONFIG_DIR_USER)

        drasticConfig = open(DRASTIC_CONFIG_PATH, "w", encoding="ascii")
        setDrasticConfig(drasticConfig, system)
        setDrasticController(drasticConfig)
        drasticConfig.close()

        chdir(DRASTIC_CONFIG_DIR_USER)
        commandArray = [DRASTIC_BIN_PATH, rom]
        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
