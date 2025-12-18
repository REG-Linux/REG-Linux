from configgen.systemFiles import HOME
from configgen.utils.videoMode import getRefreshRate
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

BIGPEMU_CONFIG_DIR = HOME + "/.bigpemu_userdata"
BIGPEMU_CONFIG_PATH = BIGPEMU_CONFIG_DIR + "/BigPEmuConfig.bigpcfg"
BIGPEMU_BIN_PATH = "/usr/bigpemu/bigpemu"


def setBigemuConfig(bigpemuConfig, system, gameResolution, playersControllers):
    # Ensure the necessary structure in the config
    if "BigPEmuConfig" not in bigpemuConfig:
        bigpemuConfig["BigPEmuConfig"] = {}
    if "Video" not in bigpemuConfig["BigPEmuConfig"]:
        bigpemuConfig["BigPEmuConfig"]["Video"] = {}

    # Adjust basic settings
    bigpemuConfig["BigPEmuConfig"]["Video"]["DisplayMode"] = 1
    bigpemuConfig["BigPEmuConfig"]["Video"]["ScreenScaling"] = 5
    bigpemuConfig["BigPEmuConfig"]["Video"]["DisplayWidth"] = gameResolution["width"]
    bigpemuConfig["BigPEmuConfig"]["Video"]["DisplayHeight"] = gameResolution["height"]
    bigpemuConfig["BigPEmuConfig"]["Video"]["DisplayFrequency"] = getRefreshRate()

    # User selections
    if system.isOptSet("bigpemu_vsync"):
        bigpemuConfig["BigPEmuConfig"]["Video"]["VSync"] = system.bigpemuConfig[
            "bigpemu_vsync"
        ]
    else:
        bigpemuConfig["BigPEmuConfig"]["Video"]["VSync"] = 1

    if system.isOptSet("bigpemu_ratio"):
        bigpemuConfig["BigPEmuConfig"]["Video"]["ScreenAspect"] = int(
            system.bigpemuConfig["bigpemu_ratio"]
        )
    else:
        bigpemuConfig["BigPEmuConfig"]["Video"]["ScreenAspect"] = 2

    bigpemuConfig["BigPEmuConfig"]["Video"]["LockAspect"] = 1


def getInGameRatio(self, config, gameResolution, rom):
    if "bigpemu_ratio" in config:
        if config["bigpemu_ratio"] == "8":
            return 16 / 9
        else:
            return 4 / 3
    else:
        return 4 / 3
