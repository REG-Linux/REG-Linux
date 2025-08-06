import utils.videoMode as videoMode
from systemFiles import HOME

BIGPEMU_CONFIG_PATH = HOME + "/.bigpemu_userdata/BigPEmuConfig.bigpcfg"
BIGPEMU_BIN_PATH = "/usr/bigpemu/bigpemu"

def setBigemuConfig(bigpemuConfig, system, gameResolution):
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
    bigpemuConfig["BigPEmuConfig"]["Video"]["DisplayFrequency"] = videoMode.getRefreshRate()

    # User selections
    if system.isOptSet("bigpemu_vsync"):
        bigpemuConfig["BigPEmuConfig"]["Video"]["VSync"] = system.bigpemuConfig["bigpemu_vsync"]
    else:
        bigpemuConfig["BigPEmuConfig"]["Video"]["VSync"] = 1
    if system.isOptSet("bigpemu_ratio"):
        bigpemuConfig["BigPEmuConfig"]["Video"]["ScreenAspect"] = int(system.bigpemuConfig["bigpemu_ratio"])
    else:
        bigpemuConfig["BigPEmuConfig"]["Video"]["ScreenAspect"] = 2
    bigpemuConfig["BigPEmuConfig"]["Video"]["LockAspect"] = 1

def getInGameRatio(self, config, gameResolution, rom):
    if "bigpemu_ratio" in config:
        if config['bigpemu_ratio'] == "8":
            return 16/9
        else:
            return 4/3
    else:
        return 4/3
