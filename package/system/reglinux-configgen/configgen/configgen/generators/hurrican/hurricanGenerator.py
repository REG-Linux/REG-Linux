from generators.Generator import Generator
from Command import Command
from os import chdir
from controllers import generate_sdl_controller_config
from utils.logger import get_logger

eslog = get_logger(__name__)


class HurricanGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        try:
            chdir("/userdata/roms/hurrican/data/levels/")
            chdir("/userdata/roms/hurrican/")
        except (FileNotFoundError, OSError) as e:
            eslog.error(
                f"ERROR: Game assets not installed. You can get them from the REG-Linux Content Downloader. Error: {str(e)}"
            )
        commandArray = ["hurrican"]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
