from generators.Generator import Generator
from Command import Command
from configparser import RawConfigParser
from os import path, makedirs
from .azaharConfig import AZAHAR_BIN_PATH, AZAHAR_CONFIG_PATH, setAzaharConfig
from .azaharControllers import setAzaharControllers

from utils.logger import get_logger
eslog = get_logger(__name__)

class AzaharGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        azaharConfig = RawConfigParser(strict=False)
        azaharConfig.optionxform=lambda optionstr: str(optionstr)

        if path.exists(AZAHAR_CONFIG_PATH):
            azaharConfig.read(AZAHAR_CONFIG_PATH)

        setAzaharConfig(azaharConfig, system)
        setAzaharControllers(azaharConfig, playersControllers)

        if not path.exists(path.dirname(AZAHAR_CONFIG_PATH)):
            makedirs(path.dirname(AZAHAR_CONFIG_PATH))
        with open(AZAHAR_CONFIG_PATH, 'w') as configfile:
            azaharConfig.write(configfile)

        commandArray = [AZAHAR_BIN_PATH, rom]
        return Command(array=commandArray)
