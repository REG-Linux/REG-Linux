from generators.Generator import Generator
from Command import Command
from os import path
from systemFiles import CONF
from controllers import generate_sdl_controller_config
from .moonlightConfig import setMoonlightConfig, MOONLIGHT_BIN_PATH, MOONLIGHT_GAMELIST_PATH, MOONLIGHT_STAGING_CONFIG_PATH

class MoonlightGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        setMoonlightConfig(system)
        gameName,confFile = self.getRealGameNameAndConfigFile(rom)
        commandArray = [MOONLIGHT_BIN_PATH, 'stream','-config',  confFile]
        commandArray.append('-app')
        commandArray.append(gameName)
        commandArray.append('-debug')

        return Command(
            array=commandArray,
            env={
                "XDG_DATA_DIRS": CONF,
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
            }
        )

    def getRealGameNameAndConfigFile(self, rom):
        # Rom's basename without extension
        romName = path.splitext(path.basename(rom))[0]
        # find the real game name
        f = open(MOONLIGHT_GAMELIST_PATH, 'r')
        gfeGame = None
        for line in f:
            try:
                gfeRom, gfeGame, confFile = line.rstrip().split(';')
                #confFile = confFile.rstrip()
            except:
                gfeRom, gfeGame = line.rstrip().split(';')
                confFile = MOONLIGHT_STAGING_CONFIG_PATH
            #If found
            if gfeRom == romName:
                # return it
                f.close()
                return [gfeGame, confFile]
        # If nothing is found (old gamelist file format ?)
        return [gfeGame, MOONLIGHT_STAGING_CONFIG_PATH]
