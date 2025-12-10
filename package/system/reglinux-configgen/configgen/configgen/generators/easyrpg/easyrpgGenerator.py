from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs
from configgen.controllers import generate_sdl_controller_config
from configgen.systemFiles import SAVES

EASYRPG_SAVE_DIR = SAVES + "/easyrpg"
EASYRPG_BIN_PATH = "/usr/bin/easyrpg-player"


class EasyRPGGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = [EASYRPG_BIN_PATH]

        # FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            commandArray.append("--show-fps")

        # Test Play (Debug Mode)
        if system.isOptSet("testplay") and system.getOptBoolean("testplay"):
            commandArray.append("--test-play")

        # Game Region (Encoding)
        if system.isOptSet("encoding") and system.config["encoding"] != "autodetect":
            commandArray.extend(["--encoding", system.config["encoding"]])
        else:
            commandArray.extend(["--encoding", "auto"])

        # Save directory
        savePath = f"{EASYRPG_SAVE_DIR}/{path.basename(rom)}"
        if not path.exists(savePath):
            makedirs(savePath)
        commandArray.extend(["--save-path", savePath])

        commandArray.extend(["--project-path", rom])

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
