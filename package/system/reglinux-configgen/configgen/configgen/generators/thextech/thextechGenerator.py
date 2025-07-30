from generators.Generator import Generator
from Command import Command
import os

class TheXTechGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        if not os.path.exists("/userdata/saves/thextech"):
                os.makedirs("/userdata/saves/thextech")

        commandArray = ["/usr/bin/thextech", "-u", "/userdata/saves/thextech"]

        # rendering_mode: sw, hw (default), vsync
        if system.isOptSet('rendering_mode'):
            commandArray.extend(["-r", system.config['rendering_mode']])

        if system.isOptSet('frameskip') and system.getOptBoolean('frameskip') == False:
            commandArray.extend(["--no-frameskip"])
        else:
            commandArray.extend(["--frameskip"])

        commandArray.extend(["-c", rom])

        return Command(array=commandArray)
