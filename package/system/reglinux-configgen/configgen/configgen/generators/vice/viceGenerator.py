from generators.Generator import Generator
from Command import Command
from os import path, makedirs
from zipfile import ZipFile
from controllers import generate_sdl_controller_config
from .viceConfig import (
    setViceConfig,
    VICE_BIN_PATH,
    VICE_CONFIG_DIR,
    VICE_CONFIG_PATH,
    VICE_CONTROLLER_PATH,
)


class ViceGenerator(Generator):
    def getResolutionMode(self, config):
        return "default"

    # Main entry of the module
    # Return command
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        if not path.exists(path.dirname(VICE_CONFIG_DIR)):
            makedirs(path.dirname(VICE_CONFIG_DIR))

        # FIXME configuration file
        # setViceConfig(VICE_CONFIG_PATH, VICE_CONTROLLER_PATH, system, metadata, guns, rom)

        # FIXME controller configuration
        # viceControllers.generateControllerConfig(system, VICE_CONFIG_PATH, playersControllers)

        commandArray = [VICE_BIN_PATH + system.config["core"]]
        # Determine the way to launch roms based on extension type
        rom_extension = path.splitext(rom)[1].lower()
        # determine extension if a zip file
        if rom_extension == ".zip":
            with ZipFile(rom, "r") as zip_file:
                for zip_info in zip_file.infolist():
                    rom_extension = path.splitext(zip_info.filename)[1]

        commandArray.append(rom)

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
