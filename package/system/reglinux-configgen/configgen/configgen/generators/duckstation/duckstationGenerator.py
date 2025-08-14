from generators.Generator import Generator
from Command import Command
from configparser import ConfigParser
from os import path, makedirs
from .duckstationConfig import DUCKSTATION_NOGUI_PATH, DUCKSTATION_BIN_PATH, DUCKSTATION_CONFIG_PATH, setDuckstationConfig
from .duckstationControllers import setDuckstationControllers

class DuckstationGenerator(Generator):
    # Duckstation is now QT-only, requires wayland compositor to run
    def requiresWayland(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        duckstatonConfig = ConfigParser(interpolation=None)
        duckstatonConfig.optionxform=lambda optionstr: str(optionstr)

        if path.exists(DUCKSTATION_CONFIG_PATH):
            duckstatonConfig.read(DUCKSTATION_CONFIG_PATH)

        setDuckstationConfig(duckstatonConfig, system, playersControllers)
        setDuckstationControllers(duckstatonConfig, system, metadata, guns, playersControllers)

        # Save config
        if not path.exists(path.dirname(DUCKSTATION_CONFIG_PATH)):
            makedirs(path.dirname(DUCKSTATION_CONFIG_PATH))
        with open(DUCKSTATION_CONFIG_PATH, 'w') as configfile:
            duckstatonConfig.write(configfile)

        # Test if it's a m3u file
        if path.splitext(rom)[1] == ".m3u":
            rom = rewriteM3uFullPath(rom)

        if path.exists(DUCKSTATION_BIN_PATH):
            commandArray = [DUCKSTATION_BIN_PATH, rom]
        else:
            commandArray = [DUCKSTATION_NOGUI_PATH, "-batch", "-fullscreen", "--", rom]

        return Command(array=commandArray)

def rewriteM3uFullPath(m3u):                                                                    # Rewrite a clean m3u file with valid fullpath
    # get initialm3u
    firstline = open(m3u).readline().rstrip()                                                   # Get first line in m3u
    initialfirstdisc = "/tmp/" + path.splitext(path.basename(firstline))[0] + ".m3u"      # Generating a temp path with the first iso filename in m3u

    # create a temp m3u to bypass Duckstation m3u bad pathfile
    fulldirname = path.dirname(m3u)
    initialm3u = open(m3u, "r")

    with open(initialfirstdisc, 'a') as f1:
        for line in initialm3u:
            if line[0] == "/":                          # for /MGScd1.chd
                newpath = fulldirname + line
            else:
                newpath = fulldirname + "/" + line      # for MGScd1.chd
            f1.write(newpath)

    return initialfirstdisc
