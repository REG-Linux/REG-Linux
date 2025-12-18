from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import mkdir, chdir, path
from codecs import open
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import CONF, SAVES
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

ECWOLF_CONFIG_DIR = CONF + "/ecwolf"
ECWOLF_CONFIG_PATH = ECWOLF_CONFIG_DIR + "/ecwolf.cfg"
ECWOLF_SAVES_DIR = SAVES + "/ecwolf"
ECWOLF_BIN_PATH = "/usr/bin/ecwolf"


class ECWolfGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        ecwolfSaves = ECWOLF_SAVES_DIR + path.basename(rom)
        command_array = [ECWOLF_BIN_PATH]  # Binary for command array

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
                eslog.error(f"Error: couldn't go into directory {rom} ({e})")

        # File method .ecwolf (recommended) for command parameters, first argument is path to dataset, next parameters according ecwolf --help
        # File method .pk3, put pk3 files next to wl6 dataset and start the mod in ES
        if path.isfile(rom):
            chdir(path.dirname(rom))
            fextension = (path.splitext(rom)[1]).lower()

            if fextension == ".ecwolf":
                try:
                    with open(rom, "r", encoding="utf-8") as f:
                        command_array += f.readline().split()
                except (IOError, IndexError) as e:
                    eslog.error(f"Error reading .ecwolf file {rom}: {e}")
                    # Ensure we handle the case where the file might be empty or inaccessible
                    pass

                # If 1. parameter isn't an argument then assume it's a path
                if not "--" in command_array[1]:
                    try:
                        chdir(command_array[1])
                    except Exception as e:
                        eslog.error(
                            f"Error: couldn't go into directory {command_array[1]} ({e})"
                        )
                    command_array.pop(1)

            if fextension == ".pk3":
                command_array += ["--file", path.basename(rom)]

        command_array += ["--savedir", ecwolfSaves]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
