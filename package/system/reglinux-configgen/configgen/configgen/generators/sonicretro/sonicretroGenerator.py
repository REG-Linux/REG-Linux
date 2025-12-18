from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import chdir
from .sonicretroConfig import setSonicretroConfig
from configgen.controllers import generate_sdl_controller_config


class SonicRetroGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Determine the emulator to use
        if (rom.lower()).endswith("son"):
            emu = "sonic2013"
        else:
            emu = "soniccd"

        setSonicretroConfig(system, emu, rom)

        # Ensure the ROM directory is the current working directory
        chdir(rom)
        command_array = [emu]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
