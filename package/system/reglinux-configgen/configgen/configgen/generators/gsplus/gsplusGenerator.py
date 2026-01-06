from pathlib import Path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.settings import UnixSettings
from configgen.systemFiles import BIOS, CONF

GSPLUS_CONFIG_DIR = str(Path(CONF) / "GSplus")
GSPLUS_CONFIG_PATH = str(Path(GSPLUS_CONFIG_DIR) / "config.txt")
GSPLUS_BIOS_DIR = str(BIOS)
GSPLUS_BIN_PATH = "/usr/bin/GSplus"


class GSplusGenerator(Generator):
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
        config_dir_path = Path(GSPLUS_CONFIG_DIR)
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True, exist_ok=True)

        config = UnixSettings(GSPLUS_CONFIG_PATH, separator=" ")
        rombase = Path(rom).name
        romext = Path(rombase).suffix

        if romext.lower() in [".dsk", ".do", ".nib"]:
            config.save("s6d1", rom)
            config.save("s5d1", "")
            config.save("s7d1", "")
            config.save("bram1[00]", "00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00")
            config.save("bram1[10]", "00 00 07 06 02 01 01 00 00 00 0f 06 06 00 05 06")
            config.save("bram1[20]", "01 00 00 00 00 00 00 01 06 00 00 00 03 02 02 02")
            config.save("bram1[30]", "00 00 00 00 00 00 00 00 00 00 01 02 03 04 05 06")
            config.save("bram1[40]", "07 00 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d")
            config.save("bram1[50]", "0e 0f ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[60]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[70]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[80]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[90]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[a0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[b0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[c0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[d0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[e0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[f0]", "ff ff ff ff ff ff ff ff ff ff ff ff fe 17 54 bd")
            config.save("bram3[00]", "00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00")
            config.save("bram3[10]", "00 00 07 06 02 01 01 00 00 00 0f 06 00 00 05 06")
            config.save("bram3[20]", "01 00 00 00 00 00 00 01 00 00 00 00 05 02 02 00")
            config.save("bram3[30]", "00 00 2d 2d 00 00 00 00 00 00 02 02 02 06 08 00")
            config.save("bram3[40]", "01 02 03 04 05 06 07 0a 00 01 02 03 04 05 06 07")
            config.save("bram3[50]", "08 09 0a 0b 0c 0d 0e 0f 00 00 ff ff ff ff ff ff")
            config.save("bram3[60]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[70]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[80]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[90]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[a0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[b0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[c0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[d0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[e0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram3[f0]", "ff ff ff ff ff ff ff ff ff ff ff ff 05 cf af 65")
        else:  # .po and .2mg
            config.save("s7d1", rom)
            config.save("s5d1", "")
            config.save("s6d1", "")
            config.save("bram1[00]", "00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00")
            config.save("bram1[10]", "00 00 07 06 02 01 01 00 00 00 0f 06 06 00 05 06")
            config.save("bram1[20]", "01 00 00 00 00 00 00 01 00 00 00 00 03 02 02 02")
            config.save("bram1[30]", "00 00 00 00 00 00 00 00 08 00 01 02 03 04 05 06")
            config.save("bram1[40]", "07 0a 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d")
            config.save("bram1[50]", "0e 0f ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[60]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[70]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[80]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[90]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[a0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[b0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[c0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[d0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[e0]", "ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff")
            config.save("bram1[f0]", "ff ff ff ff ff ff ff ff ff ff ff ff 13 24 b9 8e")
            config.save("bram3[00]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[10]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[20]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[30]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[40]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[50]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[60]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[70]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[80]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[90]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[a0]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[b0]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[c0]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[d0]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[e0]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            config.save("bram3[f0]", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
        config.save("g_cfg_rom_path", GSPLUS_BIOS_DIR)
        config.write()

        command_array = [GSPLUS_BIN_PATH, "-fullscreen"]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )
