#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os.path
import zipfile
import batoceraFiles
import controllersConfig
from . import viceConfig
from . import viceControllers

class ViceGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        if not os.path.exists(os.path.dirname(viceConfig.viceConfig)):
            os.makedirs(os.path.dirname(viceConfig.viceConfig))

        # configuration file
        viceConfig.setViceConfig(viceConfig.viceConfig, system, metadata, guns, rom)

        # controller configuration
        viceControllers.generateControllerConfig(system, viceConfig.viceConfig, playersControllers)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']] + system.config['core']]
        # Determine the way to launch roms based on extension type
        rom_extension = os.path.splitext(rom)[1].lower()
        # determine extension if a zip file
        if rom_extension == ".zip":
            with zipfile.ZipFile(rom, "r") as zip_file:
                for zip_info in zip_file.infolist():
                    rom_extension = os.path.splitext(zip_info.filename)[1]

        # TODO - add some logic for various extension types

        commandArray.append(rom)

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME":batoceraFiles.CONF,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
