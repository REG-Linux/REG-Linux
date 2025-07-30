import os
import json
import utils.videoMode as videoMode
from systemFiles import HOME

bigpemuConfig = HOME + "/.bigpemu_userdata/BigPEmuConfig.bigpcfg"
bigpemuBin = "/usr/bigpemu/bigpemu"

def getInGameRatio(self, config, gameResolution, rom):
    if "bigpemu_ratio" in config:
        if config['bigpemu_ratio'] == "8":
            return 16/9
        else:
            return 4/3
    else:
        return 4/3

def readWriteFile(system, gameResolution, playersControllers):
    # Create the directory if it doesn't exist
    if not os.path.exists(bigpemuConfig):
        os.makedirs(bigpemuConfig)

    # Delete the config file to update controllers
    # As it doesn't like to be updated
    # ¯\_(ツ)_/¯
    if os.path.exists(bigpemuConfig):
        os.remove(bigpemuConfig)

    # Create the config file as it doesn't exist
    if not os.path.exists(bigpemuConfig):
        with open(bigpemuConfig, "w") as file:
            json.dump({}, file)

    # Load or initialize the configuration
    with open(bigpemuConfig, "r") as file:
        try:
            config = json.load(file)
        except json.decoder.JSONDecodeError:
            config = {}

    # Ensure the necessary structure in the config
    if "BigPEmuConfig" not in config:
        config["BigPEmuConfig"] = {}
    if "Video" not in config["BigPEmuConfig"]:
        config["BigPEmuConfig"]["Video"] = {}

    # Adjust basic settings
    config["BigPEmuConfig"]["Video"]["DisplayMode"] = 2
    config["BigPEmuConfig"]["Video"]["ScreenScaling"] = 5
    config["BigPEmuConfig"]["Video"]["DisplayWidth"] = gameResolution["width"]
    config["BigPEmuConfig"]["Video"]["DisplayHeight"] = gameResolution["height"]
    config["BigPEmuConfig"]["Video"]["DisplayFrequency"] = videoMode.getRefreshRate()

    # User selections
    if system.isOptSet("bigpemu_vsync"):
        config["BigPEmuConfig"]["Video"]["VSync"] = system.config["bigpemu_vsync"]
    else:
        config["BigPEmuConfig"]["Video"]["VSync"] = 1
    if system.isOptSet("bigpemu_ratio"):
        config["BigPEmuConfig"]["Video"]["ScreenAspect"] = int(system.config["bigpemu_ratio"])
    else:
        config["BigPEmuConfig"]["Video"]["ScreenAspect"] = 2
    config["BigPEmuConfig"]["Video"]["LockAspect"] = 1

    with open(bigpemuConfig, "w") as file:
        json.dump(config, file, indent=4)
