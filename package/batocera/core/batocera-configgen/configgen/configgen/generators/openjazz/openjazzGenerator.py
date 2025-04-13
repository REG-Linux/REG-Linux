#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import controllersConfig

class OpenJazzGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/openjazz/")
        except:
            eslog.error("ERROR: Game assets not installed. You can install your own or get them from the Content Downloader.")
        commandArray = ["OpenJazz", "-f", "/userdata/roms/openjazz/" + rom]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
