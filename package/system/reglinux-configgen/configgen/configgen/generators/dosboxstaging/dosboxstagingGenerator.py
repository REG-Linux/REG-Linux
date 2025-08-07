from generators.Generator import Generator
from Command import Command
from os import path
from .dosboxstagingConfig import DOSBOXSTAGING_CONFIG_PATH, DOSBOXSTAGING_BIN_PATH

class DosBoxStagingGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Find rom path
        gameDir = rom
        batFile = gameDir + "/dosbox.bat"
        gameConfFile = gameDir + "/dosbox.cfg"

        commandArray = [DOSBOXSTAGING_BIN_PATH,
			"-fullscreen",
			"-userconf",
			"-exit",
			f"""{batFile}""",
			"-c", f"""set ROOT={gameDir}"""]
        if path.isfile(gameConfFile):
            commandArray.append("-conf")
            commandArray.append(f"""{gameConfFile}""")
        else:
            commandArray.append("-conf")
            commandArray.append(f"""{DOSBOXSTAGING_CONFIG_PATH}""")

        return Command(array=commandArray)
