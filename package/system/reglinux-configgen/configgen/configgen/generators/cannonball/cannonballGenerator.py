from generators.Generator import Generator
from Command import Command
from os import path, makedirs, linesep
from codecs import open
from xml.dom import minidom
from .cannonballConfig import CANNONBALL_BIN_PATH, CANNONBALL_CONFIG_PATH, setCannonballConfig

class CannonballGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if not path.exists(path.dirname(CANNONBALL_CONFIG_PATH)):
            makedirs(path.dirname(CANNONBALL_CONFIG_PATH))

        # config file
        cannoballConfig = minidom.Document()
        if path.exists(CANNONBALL_CONFIG_PATH):
            try:
                cannoballConfig = minidom.parse(CANNONBALL_CONFIG_PATH)
            except:
                pass # reinit the file

        # cannonball config file
        setCannonballConfig(cannoballConfig, system)

        # save the config file
        cannonballXml = open(CANNONBALL_CONFIG_PATH, "w", "utf-8")
        dom_string = linesep.join([s for s in cannoballConfig.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
        cannonballXml.write(dom_string)
        cannonballXml.close()

        # command line
        commandArray = [CANNONBALL_BIN_PATH]

        return Command(array=commandArray)
