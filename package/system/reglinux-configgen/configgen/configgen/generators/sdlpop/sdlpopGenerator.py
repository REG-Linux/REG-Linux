from generators.Generator import Generator
from Command import Command
import os
import shutil
from systemFiles import CONF

sdlpopConfigDir = CONF + '/SDLPoP'
sdlpopSrcCfg = sdlpopConfigDir + '/SDLPoP.cfg'
sdlpopSrcIni = sdlpopConfigDir + '/SDLPoP.ini'
sdlpopDestCfg = '/usr/share/SDLPoP/cfg/SDLPoP.cfg'
sdlpopDestIni = '/usr/share/SDLPoP/cfg/SDLPoP.ini'

class SdlPopGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["SDLPoP"]

        # create sdlpop config directory
        if not os.path.exists(sdlpopConfigDir):
            os.makedirs(sdlpopConfigDir)
        if not os.path.exists(sdlpopSrcCfg):
            shutil.copyfile('/usr/share/SDLPoP/cfg/SDLPoP.cfg', sdlpopSrcCfg)
        if not os.path.exists(sdlpopSrcIni):
            shutil.copyfile('/usr/share/SDLPoP/cfg/SDLPoP.ini', sdlpopSrcIni)
        # symbolic link cfg files
        if not os.path.exists(sdlpopDestCfg):
            os.symlink(sdlpopSrcCfg, sdlpopDestCfg)
        if not os.path.exists(sdlpopDestIni):
            os.symlink(sdlpopSrcIni, sdlpopDestIni)
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

        return Command(array=commandArray)
