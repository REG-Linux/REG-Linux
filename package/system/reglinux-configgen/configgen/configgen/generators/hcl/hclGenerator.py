from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import chdir
from configgen.controllers import generate_sdl_controller_config
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class HclGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        try:
            chdir("/userdata/roms/hcl/data/map")
            chdir("/userdata/roms/hcl/")
        except (FileNotFoundError, OSError) as e:
            eslog.error(
                f"ERROR: Game assets not installed. You can get them from the Batocera Content Downloader. Error: {str(e)}"
            )
        commandArray = ["hcl", "-d"]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
