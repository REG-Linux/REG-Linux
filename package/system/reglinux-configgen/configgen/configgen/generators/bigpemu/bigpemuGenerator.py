from generators.Generator import Generator
from Command import Command
from os import path, makedirs
from json import decoder, load, dump
from .bigpemuConfig import BIGPEMU_BIN_PATH, BIGPEMU_CONFIG_PATH, setBigemuConfig

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Create the directory if it doesn't exist
        config_dir = path.dirname(BIGPEMU_CONFIG_PATH)
        if not path.exists(config_dir):
            makedirs(config_dir)

        # Initialize the config file if it doesn't exist or is invalid
        if not path.exists(BIGPEMU_CONFIG_PATH):
            bigpemuConfig = {}
        else:
            try:
                with open(BIGPEMU_CONFIG_PATH, "r") as file:
                    bigpemuConfig = load(file)
            except (decoder.JSONDecodeError, IOError):
                bigpemuConfig = {}

        # Update configuration
        setBigemuConfig(bigpemuConfig, system, gameResolution)

        # Write the updated configuration
        with open(BIGPEMU_CONFIG_PATH, "w") as file:
            dump(bigpemuConfig, file, indent=4)

        commandArray = [BIGPEMU_BIN_PATH, rom]
        return Command(array=commandArray)
