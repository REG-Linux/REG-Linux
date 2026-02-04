from glob import glob

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

SH_BIN_PATH = "/bin/bash"

eslog = get_logger(__name__)


class ShGenerator(Generator):
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
        # in case of squashfs, the root directory is passed
        shInDir = glob(rom + "/run.sh")
        shrom = shInDir[0] if len(shInDir) == 1 else rom

        command_array = [SH_BIN_PATH, shrom]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )

    def getMouseMode(self, config, rom):
        return True
