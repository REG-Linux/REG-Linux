#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import controllers as controllersConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class HurricanGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/hurrican/data/levels/")
            os.chdir("/userdata/roms/hurrican/")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the REG-Linux Content Downloader.")
        commandArray = ["hurrican"]

        return Command.Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generate_sdl_controller_config(playersControllers)
                    })
