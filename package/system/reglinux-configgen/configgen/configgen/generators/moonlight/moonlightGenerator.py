#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os.path
import systemFiles
import controllers as controllersConfig
from . import moonlightConfig

class MoonlightGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        moonlightConfig.generateMoonlightConfig(system)
        gameName,confFile = self.getRealGameNameAndConfigFile(rom)
        commandArray = [moonlightConfig.moonlightBin, 'stream','-config',  confFile]
        commandArray.append('-app')
        commandArray.append(gameName)
        commandArray.append('-debug')

        # write our own gamecontrollerdb.txt file before launching the game
        dbfile = "/usr/share/moonlight/gamecontrollerdb.txt"
        controllersConfig.writeSDLGameDBAllControllers(playersControllers, dbfile)

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_DIRS": systemFiles.CONF
            }
        )

    def getRealGameNameAndConfigFile(self, rom):
        # Rom's basename without extension
        romName = os.path.splitext(os.path.basename(rom))[0]
        # find the real game name
        f = open(moonlightConfig.moonlightGamelist, 'r')
        gfeGame = None
        for line in f:
            try:
                gfeRom, gfeGame, confFile = line.rstrip().split(';')
                #confFile = confFile.rstrip()
            except:
                gfeRom, gfeGame = line.rstrip().split(';')
                confFile = moonlightConfig.moonlightStagingConfigFile
            #If found
            if gfeRom == romName:
                # return it
                f.close()
                return [gfeGame, confFile]
        # If nothing is found (old gamelist file format ?)
        return [gfeGame, moonlightConfig.moonlightStagingConfigFile]
