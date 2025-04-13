#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import controllersConfig

class AbuseGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["abuse", "-datadir", "/userdata/roms/abuse/abuse_data"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
