from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import CONF, SAVES, ROMS

DEVILUTIONX_CONFIG_DIR = CONF + "/devilutionx"
DEVILUTIONX_SAVES_DIR = SAVES + "/devilutionx"
DEVILUTIONX_ROMS_DIR = ROMS + "/devilutionx"
DEVILUTIONX_BIN_PATH = "/usr/bin/devilutionx"


class DevilutionXGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = [
            DEVILUTIONX_BIN_PATH,
            "--data-dir",
            DEVILUTIONX_ROMS_DIR,
            "--config-dir",
            DEVILUTIONX_CONFIG_DIR,
            "--save-dir",
            DEVILUTIONX_SAVES_DIR,
        ]

        if rom.endswith("hellfire.mpq"):
            commandArray.append("--hellfire")
        elif rom.endswith("spawn.mpq"):
            commandArray.append("--spawn")
        else:
            commandArray.append("--diablo")

        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            commandArray.append("-f")

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
