from generators.Generator import Generator
from Command import Command
from os import mkdir, chdir, path
from codecs import open
from controllers import generate_sdl_controller_config
from systemFiles import CONF, SAVES

ECWOLF_CONFIG_DIR = CONF + '/ecwolf'
ECWOLF_CONFIG_PATH = ECWOLF_CONFIG_DIR + '/ecwolf.cfg'
ECWOLF_SAVES_DIR = SAVES + '/ecwolf'
ECWOLF_BIN_PATH = '/usr/bin/ecwolf'


class ECWolfGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        ecwolfSaves = ECWOLF_SAVES_DIR + path.basename(rom)
        commandArray = [ECWOLF_BIN_PATH] # Binary for command array

        # Create config folders
        if not path.isdir(ECWOLF_CONFIG_DIR):
            mkdir(ECWOLF_CONFIG_DIR)

        # Create save folder, according rom name with extension
        if not path.isdir(ecwolfSaves):
            mkdir(ecwolfSaves)

        # Use the directory method with ecwolf extension and datafiles (wl6 or sod or nh3) inside
        if path.isdir(rom):
            try:
                chdir(rom)
            # Only game directories, not .ecwolf or .pk3 files
            except Exception as e:
                print(f"Error: couldn't go into directory {rom} ({e})")

        # File method .ecwolf (recommended) for command parameters, first argument is path to dataset, next parameters according ecwolf --help
        # File method .pk3, put pk3 files next to wl6 dataset and start the mod in ES
        if path.isfile(rom):
            chdir(path.dirname(rom))
            fextension = (path.splitext(rom)[1]).lower()

            if fextension == ".ecwolf":
                f = open(rom,"r")
                commandArray += (f.readline().split())
                f.close()

                # If 1. parameter isn't an argument then assume it's a path
                if not "--" in commandArray[1]:
                    try:
                        chdir(commandArray[1])
                    except Exception as e:
                        print(f"Error: couldn't go into directory {commandArray[1]} ({e})")
                    commandArray.pop(1)

            if fextension == ".pk3":
                commandArray += ["--file", path.basename(rom)]

        commandArray +=  ["--savedir", ecwolfSaves ]

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                    })
