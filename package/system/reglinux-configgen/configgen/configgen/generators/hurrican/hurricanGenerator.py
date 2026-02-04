from os import chdir

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class HurricanGenerator(Generator):
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
        try:
            chdir("/userdata/roms/hurrican/data/levels/")
            chdir("/userdata/roms/hurrican/")
        except (FileNotFoundError, OSError) as e:
            eslog.error(
                f"ERROR: Game assets not installed. You can get them from the REG-Linux Content Downloader. Error: {e!s}",
            )
        command_array = ["hurrican"]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
