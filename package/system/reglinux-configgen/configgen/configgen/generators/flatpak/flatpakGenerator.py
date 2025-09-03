from generators.Generator import Generator
from Command import Command
import os


class FlatpakGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        romId = None
        with open(rom) as f:
            romId = str.strip(f.read())

        # bad hack in a first time to get audio for user reglinux
        os.system("chown -R root:audio /var/run/pulse")
        os.system("chmod -R g+rwX /var/run/pulse")

        # the directory monitor must exist and all the dirs must be owned by reglinux
        commandArray = ["/usr/bin/flatpak", "run", "-v", romId]
        return Command(array=commandArray)

    def getMouseMode(self, config, rom):
        return True
