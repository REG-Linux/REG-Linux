from codecs import open as codecs_open
from os import chdir
from pathlib import Path

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator
from configgen.systemFiles import CONF, SAVES
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

ECWOLF_CONFIG_DIR = str(Path(CONF) / "ecwolf")
ECWOLF_CONFIG_PATH = str(Path(ECWOLF_CONFIG_DIR) / "ecwolf.cfg")
ECWOLF_SAVES_DIR = str(Path(SAVES) / "ecwolf")
ECWOLF_BIN_PATH = "/usr/bin/ecwolf"


class ECWolfGenerator(Generator):
    def generate(
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    ):
        ecwolfSaves = str(Path(ECWOLF_SAVES_DIR) / Path(rom).name)
        command_array = [ECWOLF_BIN_PATH]  # Binary for command array

        # Create config folders
        config_dir_path = Path(ECWOLF_CONFIG_DIR)
        if not config_dir_path.is_dir():
            config_dir_path.mkdir(parents=True, exist_ok=True)

        # Create save folder, according rom name with extension
        ecwolf_saves_path = Path(ecwolfSaves)
        if not ecwolf_saves_path.is_dir():
            ecwolf_saves_path.mkdir(parents=True, exist_ok=True)

        # Use the directory method with ecwolf extension and datafiles (wl6 or sod or nh3) inside
        rom_path = Path(rom)
        if rom_path.is_dir():
            try:
                chdir(rom)
            # Only game directories, not .ecwolf or .pk3 files
            except Exception as e:
                eslog.error(f"Error: couldn't go into directory {rom} ({e})")

        # File method .ecwolf (recommended) for command parameters, first argument is path to dataset, next parameters according ecwolf --help
        # File method .pk3, put pk3 files next to wl6 dataset and start the mod in ES
        if rom_path.is_file():
            chdir(str(rom_path.parent))
            fextension = rom_path.suffix.lower()

            if fextension == ".ecwolf":
                try:
                    with codecs_open(rom, "r", encoding="utf-8") as f:
                        command_array += f.readline().split()
                except (OSError, IndexError) as e:
                    eslog.error(f"Error reading .ecwolf file {rom}: {e}")
                    # Ensure we handle the case where the file might be empty or inaccessible

                # If 1. parameter isn't an argument then assume it's a path
                if "--" not in command_array[1]:
                    try:
                        chdir(command_array[1])
                    except Exception as e:
                        eslog.error(
                            f"Error: couldn't go into directory {command_array[1]} ({e})",
                        )
                    command_array.pop(1)

            if fextension == ".pk3":
                command_array += ["--file", rom_path.name]

        command_array += ["--savedir", ecwolfSaves]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
