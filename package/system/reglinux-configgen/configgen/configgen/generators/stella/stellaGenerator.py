#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import controllersConfig

class StellaGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Launch Stella
        commandArray = ["stella " , rom ]

        return Command.Command(
            array=commandArray,
            env={'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)}
        )
