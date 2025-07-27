#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import controllers as controllersConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class HclGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/hcl/data/map")
            os.chdir("/userdata/roms/hcl/")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["hcl", "-d"]

        return Command.Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generate_sdl_controller_config(playersControllers)
                    })
