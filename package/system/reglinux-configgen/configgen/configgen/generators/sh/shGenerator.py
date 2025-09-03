from generators.Generator import Generator
from Command import Command
from glob import glob
from controllers import generate_sdl_controller_config

SH_BIN_PATH = "/bin/bash"


class ShGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # in case of squashfs, the root directory is passed
        shInDir = glob(rom + "/run.sh")
        if len(shInDir) == 1:
            shrom = shInDir[0]
        else:
            shrom = rom

        commandArray = [SH_BIN_PATH, shrom]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    def getMouseMode(self, config, rom):
        return True
