#!/usr/bin/env python3

from generators.Generator import Generator
import systemFiles
import Command
import os
from utils.logger import get_logger
from . import mednafenConfig
from . import mednafenControllers

eslog = get_logger(__name__)

class MednafenGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        if not os.path.exists(mednafenConfig.mednafenConfigDir):
            os.makedirs(mednafenConfig.mednafenConfigDir)

        # If config file already exists, delete it
        if os.path.exists(mednafenConfig.mednafenConfigFile):
            os.unlink(mednafenConfig.mednafenConfigFile)

        # Create the config file and fill it with basic data
        cfgConfig = open(mednafenConfig.mednafenConfigFile, "w")

        # Basic settings
        mednafenConfig.setMednafenConfig(cfgConfig)
        # TODO: Controls configuration
        mednafenControllers.setMednafenControllers(cfgConfig)

        # Close config file as we are done
        cfgConfig.close()

        commandArray = [mednafenConfig.mednafenBin]
        commandArray += [ rom ]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":systemFiles.CONF, "XDG_CACHE_HOME":systemFiles.SAVES})

