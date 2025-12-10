from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import chdir
from .sonicretroConfig import setSonicretroConfig
from configgen.controllers import generate_sdl_controller_config


class SonicRetroGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Determine the emulator to use
        if (rom.lower()).endswith("son"):
            emu = "sonic2013"
        else:
            emu = "soniccd"

        setSonicretroConfig(system, emu, rom)

        # Ensure the ROM directory is the current working directory
        chdir(rom)
        commandArray = [emu]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
