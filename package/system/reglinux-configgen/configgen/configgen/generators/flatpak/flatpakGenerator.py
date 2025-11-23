from generators.Generator import Generator
from Command import Command
import os
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class FlatpakGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        eslog.debug(f"Generating command for Flatpak ROM: {rom}")

        romId = None
        try:
            with open(rom) as f:
                romId = str.strip(f.read())
            eslog.debug(f"ROM ID read from file: {romId}")
        except Exception as e:
            eslog.error(f"Error reading ROM file {rom}: {str(e)}")
            raise

        # bad hack in a first time to get audio for user reglinux
        eslog.debug("Setting up PulseAudio permissions for user reglinux")
        result1 = os.system("chown -R root:audio /var/run/pulse")
        if result1 != 0:
            eslog.warning(f"chown command returned non-zero exit status: {result1}")

        result2 = os.system("chmod -R g+rwX /var/run/pulse")
        if result2 != 0:
            eslog.warning(f"chmod command returned non-zero exit status: {result2}")

        # the directory monitor must exist and all the dirs must be owned by reglinux
        commandArray = ["/usr/bin/flatpak", "run", "-v", romId]
        eslog.debug(f"Flatpak command generated: {' '.join(commandArray)}")
        return Command(array=commandArray)

    def getMouseMode(self, config, rom):
        return True
