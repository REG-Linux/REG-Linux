from generators.Generator import Generator
from Command import Command
import os
from . import ppssppConfig
from . import ppssppControllers

class PPSSPPGenerator(Generator):

    # Main entry of the module
    # Configure PPSSPP and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        ppssppConfig.writePPSSPPConfig(system)

        # Generate the controls.ini
        for index in playersControllers :
            controller = playersControllers[index]
            # We only care about player 1
            if controller.index != "1":
                continue
            ppssppControllers.generateControllerConfig(controller)
            break

        # The command to run
        commandArray = [ppssppConfig.ppssppBin]
        commandArray.append(rom)
        commandArray.append("--fullscreen")

        # Adapt the menu size to low defenition
        # I've played with this option on PC to fix menu size in Hi-Resolution and it not working fine. I'm almost sure this option break the emulator (Darknior)
        if PPSSPPGenerator.isLowResolution(gameResolution):
            commandArray.extend(["--dpi", "0.5"])

        # state_slot option
        if system.isOptSet('state_filename'):
            commandArray.append("--state={}".format(system.config['state_filename']))

        # The next line is a reminder on how to quit PPSSPP with just the HK
        #commandArray = ['/usr/bin/PPSSPP'], rom, "--escape-exit"]

        # select the correct pad
        nplayer = 1
        for _, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                commandArray.extend(["--njoy", str(pad.index)])
            nplayer = nplayer +1

        # Adjust SDL_VIDEODRIVER to run through wayland or kmsdrm
        environment= {}
        if os.getenv("XDG_SESSION_TYPE")=="wayland":
            environment["SDL_VIDEODRIVER"] = "wayland"
        else:
            environment["SDL_VIDEODRIVER"] = "kmsdrm"

        return Command(array=commandArray, env=environment)

    @staticmethod
    def isLowResolution(gameResolution):
        return gameResolution["width"] <= 480 or gameResolution["height"] <= 480
