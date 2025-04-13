#!/usr/bin/env python
import Command
import os.path
import batoceraFiles
from generators.Generator import Generator
from . import dosboxstagingConfig

class DosBoxStagingGenerator(Generator):

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Find rom path
        gameDir = rom
        batFile = gameDir + "/dosbox.bat"
        gameConfFile = gameDir + "/dosbox.cfg"

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
			"-fullscreen",
			"-userconf",
			"-exit",
			f"""{batFile}""",
			"-c", f"""set ROOT={gameDir}"""]
        if os.path.isfile(gameConfFile):
            commandArray.append("-conf")
            commandArray.append(f"""{gameConfFile}""")
        else:
            commandArray.append("-conf")
            commandArray.append(f"""{dosboxstagingConfig.dosboxStagingConfig}""")

        return Command.Command(array=commandArray)
