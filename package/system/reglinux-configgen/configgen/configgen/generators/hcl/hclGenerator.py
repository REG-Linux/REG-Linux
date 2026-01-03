from os import chdir

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class HclGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        try:
            chdir("/userdata/roms/hcl/data/map")
            chdir("/userdata/roms/hcl/")
        except (FileNotFoundError, OSError) as e:
            eslog.error(
                f"ERROR: Game assets not installed. You can get them from the Batocera Content Downloader. Error: {e!s}",
            )
        command_array = ["hcl", "-d"]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
