#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import shutil
from . import sdlpopConfig

class SdlPopGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["SDLPoP"]

        # create sdlpop config directory
        if not os.path.exists(sdlpopConfig.sdlpopConfigDir):
            os.makedirs(sdlpopConfig.sdlpopConfigDir)
        if not os.path.exists(sdlpopConfig.sdlpopSrcCfg):
            shutil.copyfile('/usr/share/SDLPoP/cfg/SDLPoP.cfg', sdlpopConfig.sdlpopSrcCfg)
        if not os.path.exists(sdlpopConfig.sdlpopSrcIni):
            shutil.copyfile('/usr/share/SDLPoP/cfg/SDLPoP.ini', sdlpopConfig.sdlpopSrcIni)
        # symbolic link cfg files
        if not os.path.exists(sdlpopConfig.sdlpopDestCfg):
            os.symlink(sdlpopConfig.sdlpopSrcCfg, sdlpopConfig.sdlpopDestCfg)
        if not os.path.exists(sdlpopConfig.sdlpopDestIni):
            os.symlink(sdlpopConfig.sdlpopSrcIni, sdlpopConfig.sdlpopDestIni)
        # create screenshots folder in /userdata
        if not os.path.exists('/userdata/screenshots/SDLPoP'):
            os.makedirs('/userdata/screenshots/SDLPoP')
        # symbolic link screenshot folder too
        if not os.path.exists('/usr/share/SDLPoP/screenshots'):
            os.symlink('/userdata/screenshots/SDLPoP', '/usr/share/SDLPoP/screenshots', target_is_directory = True)

        # pad number
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                commandArray.append(f"joynum={pad.index}")
            nplayer += 1

        return Command.Command(array=commandArray)
