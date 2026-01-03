from configparser import ConfigParser
from os import makedirs, mkdir, path
from shutil import copyfile

from configgen.Command import Command
from configgen.generators.Generator import Generator
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
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        # Write emu.cfg to map joysticks, init with the default emu.cfg
        flycastConfig = ConfigParser(interpolation=None)
        flycastConfig.optionxform = (
            lambda optionstr: optionstr
        )  # preserve case sensitivity
        if path.exists(FLYCAST_CONFIG_PATH):
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

        ### update the configuration file
        if not path.exists(path.dirname(FLYCAST_CONFIG_PATH)):
            makedirs(path.dirname(FLYCAST_CONFIG_PATH))
        with open(FLYCAST_CONFIG_PATH, "w+") as cfgfile:
            flycastConfig.write(cfgfile)
            cfgfile.close()

        # internal config
        if not path.isdir(FLYCAST_SAVES_DIR):
            mkdir(FLYCAST_SAVES_DIR)
        if not path.isdir(FLYCAST_SAVES_DIR + "/flycast"):
            mkdir(FLYCAST_SAVES_DIR + "/flycast")
        # vmuA1
        if not path.isfile(FLYCAST_VMU_A1_PATH):
            copyfile(FLYCAST_VMU_BLANK_PATH, FLYCAST_VMU_A1_PATH)
        # vmuA2
        if not path.isfile(FLYCAST_VMU_A2_PATH):
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
