from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs
from configgen.systemFiles import CONF

DXX_REBIRTH1_CONFIG_DIR = CONF + "/d1x-rebirth"
DXX_REBIRTH1_CONFIG_PATH = DXX_REBIRTH1_CONFIG_DIR + "/descent.cfg"
DXX_REBIRTH1_BIN_PATH = "/usr/bin/d1x-rebirth"

DXX_REBIRTH2_CONFIG_DIR = CONF + "/d2x-rebirth"
DXX_REBIRTH2_CONFIG_PATH = DXX_REBIRTH2_CONFIG_DIR + "/descent.cfg"
DXX_REBIRTH2_BIN_PATH = "/usr/bin/d2x-rebirth"


class DXX_RebirthGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        directory = path.dirname(rom)
        dxx_rebirth = ""
        rebirthConfigDir = ""
        rebirthConfigFile = ""

        if path.splitext(rom)[1] == ".d1x":
            dxx_rebirth = DXX_REBIRTH1_BIN_PATH
            rebirthConfigDir = DXX_REBIRTH1_CONFIG_DIR
            rebirthConfigFile = DXX_REBIRTH1_CONFIG_PATH
        elif path.splitext(rom)[1] == ".d2x":
            dxx_rebirth = DXX_REBIRTH2_BIN_PATH
            rebirthConfigDir = DXX_REBIRTH2_CONFIG_DIR
            rebirthConfigFile = DXX_REBIRTH2_CONFIG_PATH

        if not path.exists(rebirthConfigDir):
            makedirs(rebirthConfigDir)

        # Check if the file exists
        if path.isfile(rebirthConfigFile):
            # Read the contents of the file
            with open(rebirthConfigFile, "r") as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                # set resolution
                if line.startswith("ResolutionX="):
                    lines[i] = f"ResolutionX={gameResolution['width']}\n"
                elif line.startswith("ResolutionY="):
                    lines[i] = f"ResolutionY={gameResolution['height']}\n"
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

            with open(rebirthConfigFile, "w") as file:
                file.writelines(lines)

        else:
            # File doesn't exist, create it with some default values
            with open(rebirthConfigFile, "w") as file:
                file.write(f"ResolutionX={gameResolution['width']}\n")
                file.write(f"ResolutionY={gameResolution['height']}\n")
                file.write("WindowMode=0\n")
                file.write("VSync=0\n")
                file.write("TexFilt=0\n")
                file.write("TexAnisotropy=0\n")
                file.write("Multisample=0\n")

        commandArray = [dxx_rebirth, "-hogdir", directory]

        return Command(array=commandArray)

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
