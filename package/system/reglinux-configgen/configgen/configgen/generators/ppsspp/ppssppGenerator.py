from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import getenv
from .ppssppConfig import setPPSSPPConfig, PPSSPP_BIN_PATH
from .ppssppControllers import setControllerConfig


class PPSSPPGenerator(Generator):
    # Main entry of the module
    # Configure PPSSPP and return a command
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        setPPSSPPConfig(system)

        # Generate the controls.ini
        for index in playersControllers:
            controller = playersControllers[index]
            # We only care about player 1
            if controller.index != 1:
                continue
            setControllerConfig(controller)
            break

        # The command to run
        commandArray = [PPSSPP_BIN_PATH, "--fullscreen", rom]

        # Adapt the menu size to low defenition
        # I've played with this option on PC to fix menu size in Hi-Resolution and it not working fine. I'm almost sure this option break the emulator (Darknior)
        if PPSSPPGenerator.isLowResolution(gameResolution):
            commandArray.extend(["--dpi", "0.5"])

        # state_slot option
        if system.isOptSet("state_filename"):
            commandArray.append("--state={}".format(system.config["state_filename"]))

        # Adjust SDL_VIDEODRIVER to run through wayland or kmsdrm
        environment = {}
        if getenv("XDG_SESSION_TYPE") == "wayland":
            environment["SDL_VIDEODRIVER"] = "wayland"
        else:
            environment["SDL_VIDEODRIVER"] = "kmsdrm"

        return Command(array=commandArray, env=environment)

    @staticmethod
    def isLowResolution(gameResolution):
        return gameResolution["width"] <= 480 or gameResolution["height"] <= 480
