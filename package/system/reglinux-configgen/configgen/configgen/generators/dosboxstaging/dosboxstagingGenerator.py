from generators.Generator import Generator
from Command import Command
from os import path
from systemFiles import CONF

DOSBOXSTAGING_CONFIG_DIR = CONF + '/dosbox'
DOSBOXSTAGING_CONFIG_PATH = DOSBOXSTAGING_CONFIG_DIR + '/dosbox.conf'
DOSBOXSTAGING_BIN_PATH = '/usr/bin/dosbox-staging'


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
