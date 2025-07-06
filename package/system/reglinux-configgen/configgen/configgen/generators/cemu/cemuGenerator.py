#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import glob
from . import cemuConfig
from . import cemuControllers

from utils.logger import get_logger
eslog = get_logger(__name__)

class CemuGenerator(Generator):

    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    # disable hud & bezels for now - causes game issues
    def hasInternalMangoHUDCall(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # in case of squashfs, the root directory is passed
        rpxrom = rom
        paths = list(glob.iglob(os.path.join(glob.escape(rom), '**/code/*.rpx'), recursive=True))
        if len(paths) >= 1:
            rpxrom = paths[0]

        # Create the settings file
        cemuConfig.CemuConfig(cemuConfig.cemuConfigFile, system)

        # Set-up the controllers
        cemuControllers.generateControllerConfig(system, playersControllers, cemuConfig.cemuProfilesDir)

        commandArray = [cemuConfig.cemuBin, "-f", "--force-no-menubar", "-g", rpxrom]
        return Command.Command(array=commandArray)
