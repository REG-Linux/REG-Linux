from generators.Generator import Generator
from Command import Command
from codecs import open
from xml.dom import minidom
from os import path, mkdir, linesep
from glob import iglob, escape
from .cemuConfig import CEMU_BIN_PATH, CEMU_BIOS_DIR, CEMU_CONFIG_DIR, CEMU_SAVES_DIR, CEMU_CONFIG_PATH, CEMU_PROFILES_DIR, setCemuConfig
from .cemuControllers import setControllerConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class CemuGenerator(Generator):

    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    # disable hud & bezels for now - causes game issues
    def hasInternalMangoHUDCall(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # in case of squashfs/zar, the root directory is passed
        rpxrom = rom
        paths = list(iglob(path.join(escape(rom), '**/code/*.rpx'), recursive=True))
        if len(paths) >= 1:
            rpxrom = paths[0]

        # bios pack
        if not path.isdir(CEMU_BIOS_DIR):
            mkdir(CEMU_BIOS_DIR)
        if not path.isdir(CEMU_CONFIG_DIR):
            mkdir(CEMU_CONFIG_DIR)
        # graphic packs
        if not path.isdir(CEMU_SAVES_DIR + "/graphicPacks"):
            mkdir(CEMU_SAVES_DIR + "/graphicPacks")
        if not path.isdir(CEMU_CONFIG_DIR + "/controllerProfiles"):
            mkdir(CEMU_CONFIG_DIR + "/controllerProfiles")

        # Config file
        cemuConfig = minidom.Document()
        if path.exists(CEMU_CONFIG_PATH):
            try:
                cemuConfig = minidom.parse(CEMU_CONFIG_PATH)
            except:
                pass # reinit the file

        # Create the settings file
        setCemuConfig(cemuConfig, system)

        # Save the config file
        xml = open(CEMU_CONFIG_PATH, "w")

        # TODO: python 3 - workaround to encode files in utf-8
        xml = open(CEMU_CONFIG_PATH, "w", "utf-8")
        dom_string = linesep.join([s for s in cemuConfig.toprettyxml().splitlines() if s.strip()])
        xml.write(dom_string)

        # Set-up the controllers
        setControllerConfig(system, playersControllers, CEMU_PROFILES_DIR)

        commandArray = [CEMU_BIN_PATH, "-f", "--force-no-menubar", "-g", rpxrom]
        return Command(array=commandArray)
