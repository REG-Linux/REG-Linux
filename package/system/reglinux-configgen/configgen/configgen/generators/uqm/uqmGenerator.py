from configgen.generators.Generator import Generator
from os import makedirs
from configgen.Command import Command
import controllers as controllersConfig

UQM_BIN_PATH = "/usr/bin/urquan"


class UqmGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        directories = [
            "/userdata/saves/uqm",
            "/userdata/saves/uqm/teams",
            "/userdata/saves/uqm/save",
        ]

        for directory in directories:
            makedirs(directory, exist_ok=True)

        with open("/userdata/roms/uqm/version", "a"):  # Create file if does not exist
            pass

        commandArray = [
            UQM_BIN_PATH,
            "--contentdir=/userdata/roms/uqm",
            "--configdir=/userdata/saves/uqm",
        ]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
