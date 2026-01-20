from pathlib import Path
from typing import Any

from configgen.command import Command
from configgen.generators.generator import Generator
from configgen.systemFiles import CONF

DXX_REBIRTH1_CONFIG_DIR = str(Path(CONF) / "d1x-rebirth")
DXX_REBIRTH1_CONFIG_PATH = str(Path(DXX_REBIRTH1_CONFIG_DIR) / "descent.cfg")
DXX_REBIRTH1_BIN_PATH = "/usr/bin/d1x-rebirth"

DXX_REBIRTH2_CONFIG_DIR = str(Path(CONF) / "d2x-rebirth")
DXX_REBIRTH2_CONFIG_PATH = str(Path(DXX_REBIRTH2_CONFIG_DIR) / "descent.cfg")
DXX_REBIRTH2_BIN_PATH = "/usr/bin/d2x-rebirth"


class DXX_RebirthGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
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
        directory = str(Path(rom).parent)
        dxx_rebirth = ""
        rebirthConfigDir = ""
        rebirthConfigFile = ""

        if Path(rom).suffix == ".d1x":
            dxx_rebirth = DXX_REBIRTH1_BIN_PATH
            rebirthConfigDir = DXX_REBIRTH1_CONFIG_DIR
            rebirthConfigFile = DXX_REBIRTH1_CONFIG_PATH
        elif Path(rom).suffix == ".d2x":
            dxx_rebirth = DXX_REBIRTH2_BIN_PATH
            rebirthConfigDir = DXX_REBIRTH2_CONFIG_DIR
            rebirthConfigFile = DXX_REBIRTH2_CONFIG_PATH

        rebirth_config_dir_path = Path(rebirthConfigDir)
        if not rebirth_config_dir_path.exists():
            rebirth_config_dir_path.mkdir(parents=True, exist_ok=True)

        # Check if the file exists
        if Path(rebirthConfigFile).is_file():
            # Read the contents of the file
            with Path(rebirthConfigFile).open() as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                # set resolution
                if line.startswith("ResolutionX="):
                    lines[i] = f"ResolutionX={game_resolution['width']}\n"
                elif line.startswith("ResolutionY="):
                    lines[i] = f"ResolutionY={game_resolution['height']}\n"
                # fullscreen
                if line.startswith("WindowMode="):
                    lines[i] = "WindowMode=0\n"
                # vsync
                if line.startswith("VSync="):
                    if system.isOptSet("rebirth_vsync"):
                        lines[i] = f"VSync={system.config['rebirth_vsync']}\n"
                    else:
                        lines[i] = "VSync=0\n"
                # texture filtering
                if line.startswith("TexFilt="):
                    if system.isOptSet("rebirth_filtering"):
                        lines[i] = f"TexFilt={system.config['rebirth_filtering']}\n"
                    else:
                        lines[i] = "TexFilt=0\n"
                # anisotropy
                if line.startswith("TexAnisotropy="):
                    if system.isOptSet("rebirth_anisotropy"):
                        lines[i] = (
                            f"TexAnisotropy={system.config['rebirth_anisotropy']}\n"
                        )
                    else:
                        lines[i] = "TexAnisotropy=0\n"
                # 4x multisampling
                if line.startswith("Multisample="):
                    if system.isOptSet("rebirth_multisample"):
                        lines[i] = (
                            f"Multisample={system.config['rebirth_multisample']}\n"
                        )
                    else:
                        lines[i] = "Multisample=0\n"

            with Path(rebirthConfigFile).open("w") as file:
                file.writelines(lines)

        else:
            # File doesn't exist, create it with some default values
            with Path(rebirthConfigFile).open("w") as file:
                file.write(f"ResolutionX={game_resolution['width']}\n")
                file.write(f"ResolutionY={game_resolution['height']}\n")
                file.write("WindowMode=0\n")
                file.write("VSync=0\n")
                file.write("TexFilt=0\n")
                file.write("TexAnisotropy=0\n")
                file.write("Multisample=0\n")

        command_array = [dxx_rebirth, "-hogdir", directory]

        return Command(array=command_array)

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def get_in_game_ratio(
        self,
        config: Any,
        game_resolution: dict[str, int],
        rom: str,
    ) -> float:
        return 16 / 9
