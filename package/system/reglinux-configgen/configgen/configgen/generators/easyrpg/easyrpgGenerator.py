from pathlib import Path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import SAVES

EASYRPG_SAVE_DIR = str(Path(SAVES) / "easyrpg")
EASYRPG_BIN_PATH = "/usr/bin/easyrpg-player"


class EasyRPGGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        command_array = [EASYRPG_BIN_PATH]

        # FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            command_array.append("--show-fps")

        # Test Play (Debug Mode)
        if system.isOptSet("testplay") and system.getOptBoolean("testplay"):
            command_array.append("--test-play")

        # Game Region (Encoding)
        if system.isOptSet("encoding") and system.config["encoding"] != "autodetect":
            command_array.extend(["--encoding", system.config["encoding"]])
        else:
            command_array.extend(["--encoding", "auto"])

        # Save directory
        save_path = str(Path(EASYRPG_SAVE_DIR) / Path(rom).name)
        save_path_obj = Path(save_path)
        if not save_path_obj.exists():
            save_path_obj.mkdir(parents=True, exist_ok=True)
        command_array.extend(["--save-path", save_path])

        command_array.extend(["--project-path", rom])

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
