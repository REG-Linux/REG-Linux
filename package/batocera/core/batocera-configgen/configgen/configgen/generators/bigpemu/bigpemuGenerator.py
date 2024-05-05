#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import subprocess
import sys
import shutil
import stat
import configparser
import filecmp
from utils.logger import get_logger

eslog = get_logger(__name__)

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Change path
        os.chdir("/usr/bigpemu")

        # Just run the native binary in proper path
        commandArray = ["./bigpemu", rom]

        environment={
                "PWD" : "/usr/bigpemu",
                "DISPLAY" : ":0"
        }

        # run native Linux x64 build
        return Command.Command(
            array=commandArray,
            env=environment
         )
