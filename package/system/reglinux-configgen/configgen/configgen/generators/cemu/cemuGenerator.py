import xml.parsers.expat
from codecs import open
from glob import escape, iglob
from os import linesep, mkdir, path
from xml.dom import minidom

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

from .cemuConfig import (
    CEMU_BIN_PATH,
    CEMU_BIOS_DIR,
    CEMU_CONFIG_DIR,
    CEMU_CONFIG_PATH,
    CEMU_PROFILES_DIR,
    CEMU_SAVES_DIR,
    setCemuConfig,
)
from .cemuControllers import setControllerConfig

eslog = get_logger(__name__)


class CemuGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    # disable hud & bezels for now - causes game issues
    def hasInternalMangoHUDCall(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # in case of squashfs/zar, the root directory is passed
        rpxrom = rom
        paths = list(iglob(path.join(escape(rom), "**/code/*.rpx"), recursive=True))
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
            except xml.parsers.expat.ExpatError as e:
                eslog.warning(
                    f"Invalid XML in Cemu config file {CEMU_CONFIG_PATH}: {e}. Reinitializing file."
                )
                pass  # reinit the file
            except FileNotFoundError:
                eslog.warning(f"Cemu config file not found: {CEMU_CONFIG_PATH}")
                pass  # reinit the file
            except Exception as e:
                eslog.warning(
                    f"Error parsing Cemu config file {CEMU_CONFIG_PATH}: {e}. Reinitializing file."
                )
                pass  # reinit the file

        # Create the settings file
        setCemuConfig(cemuConfig, system)

        # Save the config file
        dom_string = linesep.join(
            [s for s in cemuConfig.toprettyxml().splitlines() if s.strip()]
        )
        with open(CEMU_CONFIG_PATH, "w", encoding="utf-8") as xml_file:
            xml_file.write(dom_string)

        # Set-up the controllers
        setControllerConfig(system, players_controllers, CEMU_PROFILES_DIR)

        command_array = [CEMU_BIN_PATH, "-f", "--force-no-menubar", "-g", rpxrom]

        return Command(array=command_array)
