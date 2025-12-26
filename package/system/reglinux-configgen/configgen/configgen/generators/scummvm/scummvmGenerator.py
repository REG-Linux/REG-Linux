from configparser import ConfigParser
from glob import glob
from os import makedirs, path
from typing import Any, Dict

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.systemFiles import BIOS, CONF, SCREENSHOTS

SCUMMVM_CONFIG_DIR = CONF + "/scummvm"
SCUMMVM_CONFIG_PATH = SCUMMVM_CONFIG_DIR + "/scummvm.ini"
SCUMMVM_EXTRA_DIR = BIOS + "/scummvm/extra"
SCUMMVM_BIN_PATH = "/usr/bin/scummvm"


class ScummVMGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # crete /userdata/bios/scummvm/extra folder if it doesn't exist
        if not path.exists(SCUMMVM_EXTRA_DIR):
            makedirs(SCUMMVM_EXTRA_DIR)

        # create / modify scummvm config file as needed
        scummConfig = ConfigParser()
        scummConfig.optionxform = lambda optionstr: str(optionstr)
        if path.exists(SCUMMVM_CONFIG_PATH):
            scummConfig.read(SCUMMVM_CONFIG_PATH)

        if not scummConfig.has_section("scummvm"):
            scummConfig.add_section("scummvm")
        # set gui_browser_native to false
        scummConfig.set("scummvm", "gui_browser_native", "false")

        # save the ini file
        if not path.exists(path.dirname(SCUMMVM_CONFIG_PATH)):
            makedirs(path.dirname(SCUMMVM_CONFIG_PATH))
        with open(SCUMMVM_CONFIG_PATH, "w") as configfile:
            scummConfig.write(configfile)

        # Find rom path
        if path.isdir(rom):
            # rom is a directory: must contains a <game name>.scummvm file
            romPath = rom
            romFile = glob(romPath + "/*.scummvm")[0]
            romName = path.splitext(path.basename(romFile))[0]
        else:
            # rom is a file: split in directory and file name
            romPath = path.dirname(rom)
            # Get rom name without extension
            romName = path.splitext(path.basename(rom))[0]

        # pad number
        nplayer = 1
        id = 0
        for _, pad in sorted(players_controllers.items()):
            if nplayer == 1:
                id = pad.index
            nplayer += 1

        command_array = [SCUMMVM_BIN_PATH, "-f"]

        # set the resolution
        window_width = str(game_resolution["width"])
        window_height = str(game_resolution["height"])
        command_array.append(f"--window-size={window_width},{window_height}")

        ## user options

        # scale factor
        if system.isOptSet("scumm_scale"):
            command_array.append(f"--scale-factor={system.config['scumm_scale']}")
        else:
            command_array.append("--scale-factor=3")

        # sclaer mode
        if system.isOptSet("scumm_scaler_mode"):
            command_array.append(f"--scaler={system.config['scumm_scaler_mode']}")
        else:
            command_array.append("--scaler=normal")

        #  stretch mode
        if system.isOptSet("scumm_stretch"):
            command_array.append(f"--stretch-mode={system.config['scumm_stretch']}")
        else:
            command_array.append("--stretch-mode=center")

        # renderer
        if system.isOptSet("scumm_renderer"):
            command_array.append(f"--renderer={system.config['scumm_renderer']}")
        else:
            command_array.append("--renderer=opengl")

        # language
        if system.isOptSet("scumm_language"):
            command_array.extend(["-q", f"{system.config['scumm_language']}"])
        else:
            command_array.extend(["-q", "en"])

        # logging
        command_array.append("--logfile=/userdata/system/logs/scummvm.log")

        command_array.extend(
            [
                f"--joystick={id}",
                "--screenshotspath=" + SCREENSHOTS,
                "--extrapath=" + SCUMMVM_EXTRA_DIR,
                f"--path={romPath}",
                f"{romName}",
            ]
        )

        return Command(array=command_array)

    def get_in_game_ratio(
        self, config: Any, game_resolution: Dict[str, int], rom: str
    ) -> float:
        if (
            "scumm_stretch" in config and config["scumm_stretch"] == "fit_force_aspect"
        ) or ("scumm_stretch" in config and config["scumm_stretch"] == "pixel-perfect"):
            return 4 / 3
        return 16 / 9
