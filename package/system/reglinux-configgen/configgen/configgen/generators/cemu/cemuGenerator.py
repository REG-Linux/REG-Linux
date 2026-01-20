import pathlib
import xml.parsers.expat
from codecs import open as codecs_open
from glob import escape, iglob
from os import linesep, path
from xml.dom import minidom

from configgen.command import Command
from configgen.generators.generator import Generator
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
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    ):
        # in case of squashfs/zar, the root directory is passed
        rpxrom = rom
        paths = list(iglob(path.join(escape(rom), "**/code/*.rpx"), recursive=True))
        if len(paths) >= 1:
            rpxrom = paths[0]

        # bios pack
        if not pathlib.Path(CEMU_BIOS_DIR).is_dir():
            pathlib.Path(CEMU_BIOS_DIR).mkdir()
        if not pathlib.Path(CEMU_CONFIG_DIR).is_dir():
            pathlib.Path(CEMU_CONFIG_DIR).mkdir()
        # graphic packs
        if not pathlib.Path(CEMU_SAVES_DIR + "/graphicPacks").is_dir():
            pathlib.Path(CEMU_SAVES_DIR + "/graphicPacks").mkdir()
        if not pathlib.Path(CEMU_CONFIG_DIR + "/controllerProfiles").is_dir():
            pathlib.Path(CEMU_CONFIG_DIR + "/controllerProfiles").mkdir()

        # Config file
        cemuConfig = minidom.Document()
        if pathlib.Path(CEMU_CONFIG_PATH).exists():
            try:
                cemuConfig = minidom.parse(CEMU_CONFIG_PATH)
            except xml.parsers.expat.ExpatError as e:
                eslog.warning(
                    f"Invalid XML in Cemu config file {CEMU_CONFIG_PATH}: {e}. Reinitializing file.",
                )
                # reinit the file
            except FileNotFoundError:
                eslog.warning(f"Cemu config file not found: {CEMU_CONFIG_PATH}")
                # reinit the file
            except Exception as e:
                eslog.warning(
                    f"Error parsing Cemu config file {CEMU_CONFIG_PATH}: {e}. Reinitializing file.",
                )
                # reinit the file

        # Create the settings file
        setCemuConfig(cemuConfig, system)

        # Save the config file
        dom_string = linesep.join(
            [s for s in cemuConfig.toprettyxml().splitlines() if s.strip()],
        )
        with codecs_open(CEMU_CONFIG_PATH, "w", encoding="utf-8") as xml_file:
            xml_file.write(dom_string)

        # Set-up the controllers
        setControllerConfig(system, players_controllers, CEMU_PROFILES_DIR)

        command_array = [CEMU_BIN_PATH, "-f", "--force-no-menubar", "-g", rpxrom]

        return Command(array=command_array)
