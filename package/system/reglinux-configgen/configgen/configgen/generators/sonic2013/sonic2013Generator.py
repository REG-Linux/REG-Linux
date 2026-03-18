from os import chdir

from configgen.controllers import generate_sdl_controller_config
from configgen.core import Command
from configgen.generators.generator import Generator

from .sonic2013Config import setSonic2013Config


class Sonic2013Generator(Generator):
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
        # Determine the emulator to use
        emu = "sonic2013" if (rom.lower()).endswith("son") else "soniccd"

        setSonic2013Config(system, emu, rom)

        # Ensure the ROM directory is the current working directory
        chdir(rom)
        command_array = [emu]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
