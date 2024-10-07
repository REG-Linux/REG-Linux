#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import os
from utils.logger import get_logger
from . import mednafenConfig
from . import mednafenControllers

mednafenConfigDir = batoceraFiles.HOME + "/.mednafen"
mednafenConfigFile = mednafenConfigDir + "/mednafen.cfg"

eslog = get_logger(__name__)

class MednafenGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        if not os.path.exists(mednafenConfigDir):
            os.makedirs(mednafenConfigDir)

        # If config file already exists, delete it
        if os.path.exists(mednafenConfigFile):
            os.unlink(mednafenConfigFile)

        # Create the config file and fill it with basic data
        cfgConfig = open(mednafenConfigFile, "w")

        # Basic settings
        mednafenConfig.setMednafenConfig(cfgConfig)
        # TODO: Controls configuration
        mednafenControllers.setMednafenControllers(cfgConfig)

        # Close config file as we are done
        cfgConfig.close()

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray += [ rom ]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})

