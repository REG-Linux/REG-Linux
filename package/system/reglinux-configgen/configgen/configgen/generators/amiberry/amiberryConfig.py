from typing import Any

from configgen.settings import UnixSettings
from configgen.systemFiles import BIOS, CONF, LOGDIR, SAVES, SCREENSHOTS

AMIBERRY_CONFIG_DIR = CONF + "/amiberry"
AMIBERRY_BIOS_DIR = BIOS + "/amiga"
AMIBERRY_SCREENSHOTS_DIR = SCREENSHOTS + "/amiga"
AMIBERRY_NVRAM_DIR = AMIBERRY_CONFIG_DIR + "/nvram"
AMIBERRY_PLUGINS_DIR = AMIBERRY_CONFIG_DIR + "/plugins"
AMIBERRY_LOGS_PATH = LOGDIR + "/amiberry.log"
AMIBERRY_CONFIG_PATH = AMIBERRY_CONFIG_DIR + "/conf/amiberry.conf"
AMIBERRY_BIN_PATH = "/usr/bin/amiberry"


def setAmiberryConfig(system: Any) -> None:
    amiberryConfig = UnixSettings(AMIBERRY_CONFIG_PATH)

    amiberryConfig.save("default_quit_key", "Escape")
    amiberryConfig.save("default_open_gui_key", "F12")
    amiberryConfig.save("logfile_path", AMIBERRY_LOGS_PATH)
    amiberryConfig.save("rom_path", AMIBERRY_BIOS_DIR)
    amiberryConfig.save("saveimage_dir", SAVES + "/" + system.name)
    amiberryConfig.save("savestate_dir", SAVES + "/" + system.name)
    amiberryConfig.save("screenshot_dir", AMIBERRY_SCREENSHOTS_DIR)
    amiberryConfig.save("nvram_dir", AMIBERRY_NVRAM_DIR)
    amiberryConfig.save("retroarch_config", AMIBERRY_CONFIG_PATH)
    amiberryConfig.save("plugins_dir", AMIBERRY_PLUGINS_DIR)
    amiberryConfig.save(
        "default_vkbd_transparency",
        system.config.get("amiberry_vkbd_transparency", "60"),
    )
    amiberryConfig.save(
        "default_vkbd_language", system.config.get("amiberry_vkbd_language", "US")
    )
    amiberryConfig.save("default_vkbd_toggle", "leftstick")
    amiberryConfig.save("default_fullscreen_mode", "1")
    amiberryConfig.save("write_logfile", "yes")

    amiberryConfig.write()
