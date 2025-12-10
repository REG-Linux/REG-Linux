from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs, mkdir
from configparser import ConfigParser
from shutil import copyfile
from configgen.systemFiles import CONF
from .flycastConfig import (
    setFlycastConfig,
    FLYCAST_CONFIG_PATH,
    FLYCAST_SAVES_DIR,
    FLYCAST_BIOS_DIR,
    FLYCAST_VMU_BLANK_PATH,
    FLYCAST_VMU_A1_PATH,
    FLYCAST_VMU_A2_PATH,
    FLYCAST_BIN_PATH,
)


class FlycastGenerator(Generator):
    # Main entry of the module
    # Configure fba and return a command
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
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
                eslog.warning(f"Failed to decode config file {FLYCAST_CONFIG_PATH}: {e}. Using default config.")
                pass  # give up the file
            except Exception as e:
                eslog.warning(f"Error reading config file {FLYCAST_CONFIG_PATH}: {e}. Using default config.")
                pass  # give up the file

        setFlycastConfig(flycastConfig, system, gameResolution)

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
        commandArray = [FLYCAST_BIN_PATH]
        commandArray.append(rom)
        # Here is the trick to make flycast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME.
        # VMU will be in $XDG_DATA_HOME / $FLYCAST_DATADIR because it needs rw access -> /userdata/saves/dreamcast
        # $FLYCAST_BIOS_PATH is where Flaycast should find the bios files
        # controller cfg files are set with an absolute path, so no worry
        return Command(
            array=commandArray,
            env={
                "XDG_CONFIG_DIRS": CONF,
                "FLYCAST_DATADIR": FLYCAST_SAVES_DIR,
                "FLYCAST_BIOS_PATH": FLYCAST_BIOS_DIR,
            },
        )
