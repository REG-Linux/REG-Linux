#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import controllersConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class StellaGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Launch Stella
        commandArray = ["stella " , rom ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
