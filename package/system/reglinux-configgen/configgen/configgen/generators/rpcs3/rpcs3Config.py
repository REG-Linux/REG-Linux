from pathlib import Path

from configgen.systemFiles import CONF, ROMS, SAVES

RPCS3_CONFIG_DIR = str(CONF / "rpcs3")
RPCS3_SAVES_DIR = str(SAVES)
RPCS3_ROMS_DIR = str(ROMS / "ps3")
RPCS3_INPUT_DIR = str(CONF / "rpcs3" / "input_configs" / "global")
RPCS3_ICON_TARGET_DIR = str(CONF / "rpcs3" / "Icons")
RPCS3_CONFIG_PATH = str(CONF / "rpcs3" / "config.yml")
RPCS3_CURRENT_CONFIG_PATH = str(CONF / "rpcs3" / "GuiConfigs" / "CurrentSettings.ini")
RPCS3_PS3UPDAT_PATH = "/userdata/bios/PS3UPDAT.PUP"
RPCS3_BIN_PATH = Path("/usr/bin/rpcs3")
