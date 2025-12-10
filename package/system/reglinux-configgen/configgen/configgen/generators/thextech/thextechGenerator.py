from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs
from configgen.systemFiles import SAVES
from configgen.controllers import generate_sdl_controller_config

THEXTECH_SAVES_DIR = SAVES + "/thextech"
THEXTECH_BIN_PATH = "/usr/bin/thextech"


class TheXTechGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        if not path.exists(THEXTECH_SAVES_DIR):
            makedirs(THEXTECH_SAVES_DIR)

        commandArray = [THEXTECH_BIN_PATH, "-u", THEXTECH_SAVES_DIR]

        # rendering_mode: sw, hw (default), vsync
        if system.isOptSet("rendering_mode"):
            commandArray.extend(["-r", system.config["rendering_mode"]])

        if system.isOptSet("frameskip") and system.getOptBoolean("frameskip") == False:
            commandArray.extend(["--no-frameskip"])
        else:
            commandArray.extend(["--frameskip"])

        commandArray.extend(["-c", rom])

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )
