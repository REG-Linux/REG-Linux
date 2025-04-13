#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import configparser
import systemFiles
import os.path, shutil
from . import dosboxxConfig

class DosBoxxGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Find rom path
        gameDir = rom
        gameConfFile = gameDir + "/dosbox.cfg"

        configFile = dosboxxConfig.dosboxxConfig
        if os.path.isfile(gameConfFile):
            configFile = gameConfFile

        # configuration file
        iniSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        iniSettings.optionxform = str

        # copy config file to custom config file to avoid overwritting by dosbox-x
        customConfFile = os.path.join(dosboxxConfig.dosboxxCustom,'dosboxx-custom.conf')

        if os.path.exists(configFile):
            shutil.copy2(configFile, customConfFile)
            iniSettings.read(customConfFile)

        # sections
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # save
        with open(customConfFile, 'w') as config:
            iniSettings.write(config)

        # -fullscreen removed as it crashes on N2
        commandArray = [dosboxxConfig.dosboxxBin,
			"-exit",
			"-c", f"""mount c {gameDir}""",
                        "-c", "c:",
                        "-c", "dosbox.bat",
                        "-fastbioslogo",
                        f"-conf {customConfFile}"]

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":systemFiles.CONF})
