from os import getenv

from configgen.Command import Command
from configgen.generators.Generator import Generator

from .ppssppConfig import PPSSPP_BIN_PATH, setPPSSPPConfig
from .ppssppControllers import setControllerConfig


class PPSSPPGenerator(Generator):
    # Main entry of the module
    # Configure PPSSPP and return a command
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        setPPSSPPConfig(system)

        # Generate the controls.ini
        for index in players_controllers:
            controller = players_controllers[index]
            # We only care about player 1
            if controller.index != 1:
                continue
            setControllerConfig(controller)
            break

        # The command to run
        command_array = [str(PPSSPP_BIN_PATH), "--fullscreen", rom]

        # Adapt the menu size to low defenition
        # I've played with this option on PC to fix menu size in Hi-Resolution and it not working fine. I'm almost sure this option break the emulator (Darknior)
        if PPSSPPGenerator.isLowResolution(game_resolution):
            command_array.extend(["--dpi", "0.5"])

        # state_slot option
        if system.isOptSet("state_filename"):
            command_array.append("--state={}".format(system.config["state_filename"]))

        # Adjust SDL_VIDEODRIVER to run through wayland or kmsdrm
        environment = {}
        if getenv("XDG_SESSION_TYPE") == "wayland":
            environment["SDL_VIDEODRIVER"] = "wayland"
        else:
            environment["SDL_VIDEODRIVER"] = "kmsdrm"

        return Command(array=command_array, env=environment)

    @staticmethod
    def isLowResolution(game_resolution: dict[str, int]) -> bool:
        return game_resolution["width"] <= 480 or game_resolution["height"] <= 480
