from pathlib import Path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF, ROMS, SAVES

DEVILUTIONX_CONFIG_DIR = str(Path(CONF) / "devilutionx")
DEVILUTIONX_SAVES_DIR = str(Path(SAVES) / "devilutionx")
DEVILUTIONX_ROMS_DIR = str(Path(ROMS) / "devilutionx")
DEVILUTIONX_BIN_PATH = "/usr/bin/devilutionx"


class DevilutionXGenerator(Generator):
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
        command_array = [
            DEVILUTIONX_BIN_PATH,
            "--data-dir",
            DEVILUTIONX_ROMS_DIR,
            "--config-dir",
            DEVILUTIONX_CONFIG_DIR,
            "--save-dir",
            DEVILUTIONX_SAVES_DIR,
        ]

        if rom.endswith("hellfire.mpq"):
            command_array.append("--hellfire")
        elif rom.endswith("spawn.mpq"):
            command_array.append("--spawn")
        else:
            command_array.append("--diablo")

        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            command_array.append("-f")

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
