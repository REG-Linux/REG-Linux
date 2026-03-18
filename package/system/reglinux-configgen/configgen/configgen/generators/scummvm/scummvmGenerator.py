from configparser import ConfigParser
from glob import glob
from pathlib import Path
from typing import Any

from configgen.config.paths import BIOS, CONF, SCREENSHOTS
from configgen.core import Command
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

SCUMMVM_CONFIG_DIR = str(CONF / "scummvm")
SCUMMVM_CONFIG_PATH = str(CONF / "scummvm" / "scummvm.ini")
SCUMMVM_EXTRA_DIR = str(BIOS / "scummvm" / "extra")
SCUMMVM_BIN_PATH = "/usr/bin/scummvm"


class ScummVMGenerator(Generator):
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
        # create / modify scummvm config file as needed
        scummConfig = ConfigParser()
        scummConfig.optionxform = lambda optionstr: str(optionstr)
        config_path = Path(SCUMMVM_CONFIG_PATH)
        if config_path.exists():
            scummConfig.read(SCUMMVM_CONFIG_PATH)

        if not scummConfig.has_section("scummvm"):
            scummConfig.add_section("scummvm")
        scummConfig.set("scummvm", "gui_browser_native", "false")

        # save the ini file
        config_dir_path = config_path.parent
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)
        with Path(SCUMMVM_CONFIG_PATH).open("w") as configfile:
            scummConfig.write(configfile)

        # Find rom path and name
        rom_path = Path(rom)
        if rom_path.is_dir():
            romPath = rom
            romFile = glob(str(rom_path / "*.scummvm"))[0]
            romName = Path(romFile).stem
        else:
            romPath = str(rom_path.parent)
            romName = rom_path.stem

        eslog.debug(f"ScummVM: path={romPath}, game={romName}")

        # Get joystick id from player 1 controller
        joystick_id = 0
        for nplayer, (_key, pad) in enumerate(
            sorted(players_controllers.items()), start=1
        ):
            if nplayer == 1:
                joystick_id = pad.index
                break

        command_array = [SCUMMVM_BIN_PATH, "-f"]

        # Set resolution
        command_array.append(
            f"--window-size={game_resolution['width']},{game_resolution['height']}"
        )

        # Scale factor
        if system.isOptSet("scumm_scale"):
            command_array.append(f"--scale-factor={system.config['scumm_scale']}")
        else:
            command_array.append("--scale-factor=3")

        # Scaler mode
        if system.isOptSet("scumm_scaler_mode"):
            command_array.append(f"--scaler={system.config['scumm_scaler_mode']}")
        else:
            command_array.append("--scaler=normal")

        # Stretch mode
        if system.isOptSet("scumm_stretch"):
            command_array.append(f"--stretch-mode={system.config['scumm_stretch']}")
        else:
            command_array.append("--stretch-mode=center")

        # Renderer
        if system.isOptSet("scumm_renderer"):
            command_array.append(f"--renderer={system.config['scumm_renderer']}")
        else:
            command_array.append("--renderer=opengl")

        # Language
        if system.isOptSet("scumm_language"):
            command_array.extend(["-q", f"{system.config['scumm_language']}"])
        else:
            command_array.extend(["-q", "en"])

        # Logging
        command_array.append("--logfile=/userdata/system/logs/scummvm.log")

        command_array.extend(
            [
                f"--joystick={joystick_id}",
                "--screenshotspath=" + str(SCREENSHOTS),
                "--extrapath=" + str(SCUMMVM_EXTRA_DIR),
                f"--path={romPath}",
                f"{romName}",
            ],
        )

        return Command(array=command_array)

    def get_in_game_ratio(
        self,
        config: Any,
        game_resolution: dict[str, int],
        rom: str,
    ) -> float:
        if (
            "scumm_stretch" in config and config["scumm_stretch"] == "fit_force_aspect"
        ) or ("scumm_stretch" in config and config["scumm_stretch"] == "pixel-perfect"):
            return 4 / 3
        return 16 / 9
