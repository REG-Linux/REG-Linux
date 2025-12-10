from configgen.generators.Generator import Generator
from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from .iortcwConfig import setIortcwConfig, IORTCW_BIN_PATH


class IORTCWGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        setIortcwConfig(system, gameResolution)

        # Single Player for now
        commandArray = [IORTCW_BIN_PATH]

        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                )
            },
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
