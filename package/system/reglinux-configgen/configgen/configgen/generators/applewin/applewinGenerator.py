#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import controllers as controllersConfig
from . import applewinConfig

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [applewinConfig.applewinBin, "--no-imgui", "--d1", rom]

        return Command.Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
                    })
