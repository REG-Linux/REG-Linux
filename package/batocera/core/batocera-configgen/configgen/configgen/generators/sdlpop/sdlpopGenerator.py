#!/usr/bin/env python

from generators.Generator import Generator
import Command
import controllersConfig
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
            shutil.copyfile('/usr/share/sdlpop/cfg/SDLPoP.cfg', sdlpopConfig.sdlpopSrcCfg)
        if not os.path.exists(sdlpopConfig.sdlpopSrcIni):
            shutil.copyfile('/usr/share/sdlpop/cfg/SDLPoP.ini', sdlpopConfig.sdlpopSrcIni)
        # symbolic link cfg files
        if not os.path.exists(sdlpopConfig.sdlpopDestCfg):
            os.symlink(sdlpopConfig.sdlpopSrcCfg, sdlpopConfig.sdlpopDestCfg)
        if not os.path.exists(sdlpopConfig.sdlpopDestIni):
            os.symlink(sdlpopConfig.sdlpopSrcIni, sdlpopConfig.sdlpopDestIni)
        # symbolic link screenshot folder too
        if not os.path.exists('/userdata/screenshots/sdlpop'):
            os.makedirs('/userdata/screenshots/sdlpop')
            os.symlink('/userdata/screenshots/sdlpop', '/usr/share/sdlpop/screenshots', target_is_directory = True)

        # pad number
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                commandArray.append(f"joynum={pad.index}")
            nplayer += 1

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })
