from pathlib import Path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import BIOS

TSUGARU_BIN_PATH = "/usr/bin/Tsugaru_CUI"
TSUGARU_BIOS_DIR = str(BIOS / "fmtowns")


class TsugaruGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Start emulator fullscreen
        command_array = [TSUGARU_BIN_PATH, TSUGARU_BIOS_DIR]
        command_array += ["-AUTOSCALE", "-HIGHRES", "-NOWAITBOOT"]
        command_array += ["-GAMEPORT0", "KEY"]
        command_array += ["-KEYBOARD", "DIRECT"]
        command_array += ["-PAUSEKEY", "F10"]

        # CD Speed
        if system.isOptSet("cdrom_speed") and system.config["cdrom_speed"] != "auto":
            command_array += ["-CDSPEED", system.config["cdrom_speed"]]

        # CPU Emulation
        if system.isOptSet("386dx") and system.config["386dx"] == "1":
            command_array += ["-PRETEND386DX"]

        extension = Path(rom).suffix[1:].lower()
        if extension in ["iso", "cue", "bin"]:
            # Launch CD-ROM
            command_array += ["-CD", rom]
        else:
            # Launch floppy
            command_array += ["-FD0", rom]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
