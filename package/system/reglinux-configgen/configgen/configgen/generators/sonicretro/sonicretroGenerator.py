from os import chdir

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator

from .sonicretroConfig import setSonicretroConfig


class SonicRetroGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        # Determine the emulator to use
        emu = "sonic2013" if (rom.lower()).endswith("son") else "soniccd"

        setSonicretroConfig(system, emu, rom)

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
