import pathlib
from configparser import ConfigParser
from os import path
from shutil import copyfile

from configgen.command import Command
from configgen.generators.generator import Generator
from configgen.systemFiles import CONF
from configgen.utils.logger import get_logger

from .flycastConfig import (
    FLYCAST_BIN_PATH,
    FLYCAST_BIOS_DIR,
    FLYCAST_CONFIG_PATH,
    FLYCAST_SAVES_DIR,
    FLYCAST_VMU_A1_PATH,
    FLYCAST_VMU_A2_PATH,
    FLYCAST_VMU_BLANK_PATH,
    setFlycastConfig,
)

eslog = get_logger(__name__)


class FlycastGenerator(Generator):
    # Main entry of the module
    # Configure fba and return a command
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
        # Write emu.cfg to map joysticks, init with the default emu.cfg
        flycastConfig = ConfigParser(interpolation=None)
        flycastConfig.optionxform = lambda optionstr: (
            optionstr
        )  # preserve case sensitivity
        if pathlib.Path(FLYCAST_CONFIG_PATH).exists():
            try:
                flycastConfig.read(FLYCAST_CONFIG_PATH)
            except UnicodeDecodeError as e:
                eslog.warning(
                    f"Failed to decode config file {FLYCAST_CONFIG_PATH}: {e}. Using default config.",
                )
                # give up the file
            except Exception as e:
                eslog.warning(
                    f"Error reading config file {FLYCAST_CONFIG_PATH}: {e}. Using default config.",
                )
                # give up the file

        setFlycastConfig(flycastConfig, system, game_resolution)

        # update the configuration file
        if not pathlib.Path(path.dirname(FLYCAST_CONFIG_PATH)).exists():
            pathlib.Path(path.dirname(FLYCAST_CONFIG_PATH)).mkdir(parents=True)
        with pathlib.Path(FLYCAST_CONFIG_PATH).open("w+") as cfgfile:
            flycastConfig.write(cfgfile)
            cfgfile.close()

        # internal config
        if not pathlib.Path(FLYCAST_SAVES_DIR).is_dir():
            pathlib.Path(FLYCAST_SAVES_DIR).mkdir()
        if not pathlib.Path(FLYCAST_SAVES_DIR + "/flycast").is_dir():
            pathlib.Path(FLYCAST_SAVES_DIR + "/flycast").mkdir()
        # vmuA1
        if not pathlib.Path(FLYCAST_VMU_A1_PATH).is_file():
            copyfile(FLYCAST_VMU_BLANK_PATH, FLYCAST_VMU_A1_PATH)
        # vmuA2
        if not pathlib.Path(FLYCAST_VMU_A2_PATH).is_file():
            copyfile(FLYCAST_VMU_BLANK_PATH, FLYCAST_VMU_A2_PATH)

        # the command to run
        command_array = [FLYCAST_BIN_PATH]
        command_array.append(rom)
        # Here is the trick to make flycast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME.
        # VMU will be in $XDG_DATA_HOME / $FLYCAST_DATADIR because it needs rw access -> /userdata/saves/dreamcast
        # $FLYCAST_BIOS_PATH is where Flaycast should find the bios files
        # controller cfg files are set with an absolute path, so no worry
        return Command(
            array=command_array,
            env={
                "XDG_CONFIG_DIRS": str(CONF),
                "FLYCAST_DATADIR": FLYCAST_SAVES_DIR,
                "FLYCAST_BIOS_PATH": FLYCAST_BIOS_DIR,
            },
        )
