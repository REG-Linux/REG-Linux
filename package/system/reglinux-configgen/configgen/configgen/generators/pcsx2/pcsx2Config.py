from configparser import ConfigParser
from os import path, makedirs, remove
from json import loads
from requests import get
from time import time
from shutil import copyfile
from subprocess import check_output, CalledProcessError
from systemFiles import CONF, BIOS
from .pcsx2Controllers import (
    getWheelType,
    useEmulatorWheels,
    wheelTypeMapping,
    input2wheel,
)
from utils.logger import get_logger

PCSX2_CONFIG_DIR = CONF + "/PCSX2"
PCSX2_BIOS_DIR = BIOS + "/ps2"
PCSX2_BIN_PATH = "/usr/pcsx2/bin/pcsx2-qt"
PCSX2_PATCHES_PATH = PCSX2_BIOS_DIR + "/patches.zip"
PCSX2_SOURCE_PATH = "/usr/share/reglinux/datainit/bios/ps2/patches.zip"


eslog = get_logger(__name__)


def getInGameRatio(self, config, gameResolution, rom):
    if getGfxRatioFromConfig(config, gameResolution) == "16:9" or (
        getGfxRatioFromConfig(config, gameResolution) == "Stretch"
        and gameResolution["width"] / float(gameResolution["height"])
        > ((16.0 / 9.0) - 0.1)
    ):
        return 16 / 9
    return 4 / 3


def getGfxRatioFromConfig(config, gameResolution):
    # 2: 4:3 ; 1: 16:9
    if "pcsx2_ratio" in config:
        if config["pcsx2_ratio"] == "16:9":
            return "16:9"
        elif config["pcsx2_ratio"] == "full":
            return "Stretch"
    return "4:3"


def setPcsx2Reg():
    configFileName = "{}/{}".format(PCSX2_CONFIG_DIR, "PCSX2-reg.ini")
    if not path.exists(PCSX2_CONFIG_DIR):
        makedirs(PCSX2_CONFIG_DIR)
    f = open(configFileName, "w")
    f.write("DocumentsFolderMode=User\n")
    f.write("CustomDocumentsFolder=/usr/pcsx2/bin\n")
    f.write("UseDefaultSettingsFolder=enabled\n")
    f.write("SettingsFolder=/userdata/system/configs/PCSX2/inis\n")
    f.write("Install_Dir=/usr/pcsx2/bin\n")
    f.write("RunWizard=0\n")
    f.close()


def configureAudio():
    configFileName = "{}/{}".format(PCSX2_CONFIG_DIR + "/inis", "spu2-x.ini")
    if not path.exists(PCSX2_CONFIG_DIR + "/inis"):
        makedirs(PCSX2_CONFIG_DIR + "/inis")

    # Keep the custom files
    if path.exists(configFileName):
        return

    f = open(configFileName, "w")
    f.write("[MIXING]\n")
    f.write("Interpolation=1\n")
    f.write("Disable_Effects=0\n")
    f.write("[OUTPUT]\n")
    f.write("Output_Module=SDLAudio\n")
    f.write("[PORTAUDIO]\n")
    f.write("HostApi=ALSA\n")
    f.write("Device=default\n")
    f.write("[SDL]\n")
    f.write("HostApi=alsa\n")
    f.close()


def setPcsx2Config(system, rom, controllers, metadata, guns, wheels, playingWithWheel):
    configFileName = "{}/{}".format(PCSX2_CONFIG_DIR + "/inis", "PCSX2.ini")

    if not path.exists(PCSX2_CONFIG_DIR + "/inis"):
        makedirs(PCSX2_CONFIG_DIR + "/inis")

    if not path.isfile(configFileName):
        f = open(configFileName, "w")
        f.write("[UI]\n")
        f.close()

    pcsx2INIConfig = ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    pcsx2INIConfig.optionxform = lambda optionstr: str(optionstr)

    if path.isfile(configFileName):
        pcsx2INIConfig.read(configFileName)

    ## [UI]
    if not pcsx2INIConfig.has_section("UI"):
        pcsx2INIConfig.add_section("UI")

    # set the settings we want always enabled
    pcsx2INIConfig.set("UI", "SettingsVersion", "1")
    pcsx2INIConfig.set("UI", "InhibitScreensaver", "true")
    pcsx2INIConfig.set("UI", "ConfirmShutdown", "false")
    pcsx2INIConfig.set("UI", "StartPaused", "false")
    pcsx2INIConfig.set("UI", "PauseOnFocusLoss", "false")
    pcsx2INIConfig.set("UI", "StartFullscreen", "true")
    pcsx2INIConfig.set("UI", "HideMouseCursor", "true")
    pcsx2INIConfig.set("UI", "RenderToSeparateWindow", "false")
    pcsx2INIConfig.set("UI", "HideMainWindowWhenRunning", "true")
    pcsx2INIConfig.set("UI", "DoubleClickTogglesFullscreen", "false")

    ## [Folders]
    if not pcsx2INIConfig.has_section("Folders"):
        pcsx2INIConfig.add_section("Folders")

    # remove inconsistent SaveStates casing if it exists
    pcsx2INIConfig.remove_option("Folders", "SaveStates")

    # set the folders we want
    pcsx2INIConfig.set("Folders", "Bios", "../../../bios/ps2")
    pcsx2INIConfig.set("Folders", "Snapshots", "../../../screenshots")
    pcsx2INIConfig.set("Folders", "Savestates", "../../../saves/ps2/pcsx2/sstates")
    pcsx2INIConfig.set("Folders", "MemoryCards", "../../../saves/ps2/pcsx2")
    pcsx2INIConfig.set("Folders", "Logs", "../../logs")
    pcsx2INIConfig.set("Folders", "Cheats", "../../../cheats/ps2")
    pcsx2INIConfig.set("Folders", "CheatsWS", "../../../cheats/ps2/cheats_ws")
    pcsx2INIConfig.set("Folders", "CheatsNI", "../../../cheats/ps2/cheats_ni")
    pcsx2INIConfig.set("Folders", "Cache", "../../cache/ps2")
    pcsx2INIConfig.set("Folders", "Textures", "textures")
    pcsx2INIConfig.set("Folders", "InputProfiles", "inputprofiles")
    pcsx2INIConfig.set("Folders", "Videos", "../../../saves/ps2/pcsx2/videos")

    # create cache folder
    if not path.exists("/userdata/system/cache/ps2"):
        makedirs("/userdata/system/cache/ps2")

    ## [EmuCore]
    if not pcsx2INIConfig.has_section("EmuCore"):
        pcsx2INIConfig.add_section("EmuCore")

    # set the settings we want always enabled
    pcsx2INIConfig.set("EmuCore", "EnableDiscordPresence", "false")

    # Fastboot
    if system.isOptSet("pcsx2_fastboot") and system.config["pcsx2_fastboot"] == "0":
        pcsx2INIConfig.set("EmuCore", "EnableFastBoot", "true")
    else:
        pcsx2INIConfig.set("EmuCore", "EnableFastBoot", "false")
    # Cheats
    if system.isOptSet("pcsx2_cheats"):
        pcsx2INIConfig.set("EmuCore", "EnableCheats", system.config["pcsx2_cheats"])
    else:
        pcsx2INIConfig.set("EmuCore", "EnableCheats", "false")
    # Widescreen Patches
    if system.isOptSet("pcsx2_EnableWideScreenPatches"):
        pcsx2INIConfig.set(
            "EmuCore",
            "EnableWideScreenPatches",
            system.config["pcsx2_EnableWideScreenPatches"],
        )
    else:
        pcsx2INIConfig.set("EmuCore", "EnableWideScreenPatches", "false")
    # No-interlacing Patches
    if system.isOptSet("pcsx2_interlacing_patches"):
        pcsx2INIConfig.set(
            "EmuCore",
            "EnableNoInterlacingPatches",
            system.config["pcsx2_interlacing_patches"],
        )
    else:
        pcsx2INIConfig.set("EmuCore", "EnableNoInterlacingPatches", "false")

    ## [Achievements]
    if not pcsx2INIConfig.has_section("Achievements"):
        pcsx2INIConfig.add_section("Achievements")
    pcsx2INIConfig.set("Achievements", "Enabled", "false")
    if (
        system.isOptSet("retroachievements")
        and system.getOptBoolean("retroachievements") == True
    ):
        headers = {"Content-type": "text/plain", "User-Agent": "REG-linux"}
        login_url = "https://retroachievements.org/"
        username = system.config.get("retroachievements.username", "")
        password = system.config.get("retroachievements.password", "")
        hardcore = system.config.get("retroachievements.hardcore", "")
        indicator = system.config.get("retroachievements.challenge_indicators", "")
        presence = system.config.get("retroachievements.richpresence", "")
        leaderbd = system.config.get("retroachievements.leaderboards", "")
        login_cmd = f"dorequest.php?r=login&u={username}&p={password}"
        try:
            res = get(login_url + login_cmd, headers=headers)
            if res.status_code != 200:
                eslog.warning(
                    f"ERROR: RetroAchievements.org responded with #{res.status_code} [{res.reason}]"
                )
                pcsx2INIConfig.set("Cheevos", "Enabled", "false")
            else:
                res.encoding = "utf-8"
                parsedout = loads(res.json())
                if not parsedout["Success"]:
                    eslog.warning(
                        f"ERROR: RetroAchievements login failed with ({str(parsedout)})"
                    )
                token = parsedout["Token"]
                pcsx2INIConfig.set("Achievements", "Enabled", "true")
                pcsx2INIConfig.set("Achievements", "Username", username)
                pcsx2INIConfig.set("Achievements", "Token", token)
                pcsx2INIConfig.set("Achievements", "LoginTimestamp", str(int(time())))
                if hardcore == "1":
                    pcsx2INIConfig.set("Achievements", "ChallengeMode", "true")
                else:
                    pcsx2INIConfig.set("Achievements", "ChallengeMode", "false")
                if indicator == "1":
                    pcsx2INIConfig.set("Achievements", "PrimedIndicators", "true")
                else:
                    pcsx2INIConfig.set("Achievements", "PrimedIndicators", "false")
                if presence == "1":
                    pcsx2INIConfig.set("Achievements", "RichPresence", "true")
                else:
                    pcsx2INIConfig.set("Achievements", "RichPresence", "false")
                if leaderbd == "1":
                    pcsx2INIConfig.set("Achievements", "Leaderboards", "true")
                else:
                    pcsx2INIConfig.set("Achievements", "Leaderboards", "false")
        except (Exception, ValueError) as e:
            eslog.error(f"ERROR: setting RetroAchievements parameters - {str(e)}")
    # set other settings
    pcsx2INIConfig.set("Achievements", "TestMode", "false")
    pcsx2INIConfig.set("Achievements", "UnofficialTestMode", "false")
    pcsx2INIConfig.set("Achievements", "Notifications", "true")
    pcsx2INIConfig.set("Achievements", "SoundEffects", "true")

    ## [Filenames]
    if not pcsx2INIConfig.has_section("Filenames"):
        pcsx2INIConfig.add_section("Filenames")

    ## [EMUCORE/GS]
    if not pcsx2INIConfig.has_section("EmuCore/GS"):
        pcsx2INIConfig.add_section("EmuCore/GS")

    # Renderer
    # Check Vulkan first to be sure
    try:
        have_vulkan = check_output(
            ["/usr/bin/system-vulkan", "hasVulkan"], text=True
        ).strip()
        if have_vulkan == "true":
            eslog.debug("Vulkan driver is available on the system.")
            renderer = "12"  # Default to OpenGL

            if system.isOptSet("pcsx2_gfxbackend"):
                if system.config["pcsx2_gfxbackend"] == "13":
                    eslog.debug("User selected Software! Man you must have a fast CPU!")
                    renderer = "13"
                elif system.config["pcsx2_gfxbackend"] == "14":
                    eslog.debug("User selected Vulkan")
                    renderer = "14"
                    try:
                        have_discrete = check_output(
                            ["/usr/bin/system-vulkan", "hasDiscrete"], text=True
                        ).strip()
                        if have_discrete == "true":
                            eslog.debug(
                                "A discrete GPU is available on the system. We will use that for performance"
                            )
                            try:
                                discrete_name = check_output(
                                    ["/usr/bin/system-vulkan", "discreteName"],
                                    text=True,
                                ).strip()
                                if discrete_name:
                                    eslog.debug(
                                        "Using Discrete GPU Name: {} for PCSX2".format(
                                            discrete_name
                                        )
                                    )
                                    pcsx2INIConfig.set(
                                        "EmuCore/GS", "Adapter", discrete_name
                                    )
                                else:
                                    eslog.debug("Couldn't get discrete GPU Name")
                                    pcsx2INIConfig.set(
                                        "EmuCore/GS", "Adapter", "(Default)"
                                    )
                            except CalledProcessError as e:
                                eslog.debug(
                                    "Error getting discrete GPU Name: {}".format(e)
                                )
                                pcsx2INIConfig.set("EmuCore/GS", "Adapter", "(Default)")
                        else:
                            eslog.debug(
                                "Discrete GPU is not available on the system. Using default."
                            )
                            pcsx2INIConfig.set("EmuCore/GS", "Adapter", "(Default)")
                    except CalledProcessError as e:
                        eslog.debug("Error checking for discrete GPU: {}".format(e))
            else:
                eslog.debug("User selected or defaulting to OpenGL")

            pcsx2INIConfig.set("EmuCore/GS", "Renderer", renderer)
        else:
            eslog.debug(
                "Vulkan driver is not available on the system. Falling back to OpenGL"
            )
            pcsx2INIConfig.set("EmuCore/GS", "Renderer", "12")
    except CalledProcessError as e:
        eslog.debug("Error checking for Vulkan driver: {}".format(e))

    # Ratio
    if system.isOptSet("pcsx2_ratio"):
        pcsx2INIConfig.set("EmuCore/GS", "AspectRatio", system.config["pcsx2_ratio"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "AspectRatio", "Auto 4:3/3:2")
    # Vsync
    if system.isOptSet("pcsx2_vsync"):
        pcsx2INIConfig.set("EmuCore/GS", "VsyncEnable", system.config["pcsx2_vsync"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "VsyncEnable", "0")
    # Resolution
    if system.isOptSet("pcsx2_resolution"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "upscale_multiplier", system.config["pcsx2_resolution"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "upscale_multiplier", "1")
    # FXAA
    if system.isOptSet("pcsx2_fxaa"):
        pcsx2INIConfig.set("EmuCore/GS", "fxaa", system.config["pcsx2_fxaa"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "fxaa", "false")
    # FMV Ratio
    if system.isOptSet("pcsx2_fmv_ratio"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "FMVAspectRatioSwitch", system.config["pcsx2_fmv_ratio"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "FMVAspectRatioSwitch", "Auto 4:3/3:2")
    # Mipmapping
    if system.isOptSet("pcsx2_mipmapping"):
        pcsx2INIConfig.set("EmuCore/GS", "mipmap_hw", system.config["pcsx2_mipmapping"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "mipmap_hw", "-1")
    # Trilinear Filtering
    if system.isOptSet("pcsx2_trilinear_filtering"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "TriFilter", system.config["pcsx2_trilinear_filtering"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "TriFilter", "-1")
    # Anisotropic Filtering
    if system.isOptSet("pcsx2_anisotropic_filtering"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "MaxAnisotropy", system.config["pcsx2_anisotropic_filtering"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "MaxAnisotropy", "0")
    # Dithering
    if system.isOptSet("pcsx2_dithering"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "dithering_ps2", system.config["pcsx2_dithering"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "dithering_ps2", "2")
    # Texture Preloading
    if system.isOptSet("pcsx2_texture_loading"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "texture_preloading", system.config["pcsx2_texture_loading"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "texture_preloading", "2")
    # Deinterlacing
    if system.isOptSet("pcsx2_deinterlacing"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "deinterlace_mode", system.config["pcsx2_deinterlacing"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "deinterlace_mode", "0")
    # Anti-Blur
    if system.isOptSet("pcsx2_blur"):
        pcsx2INIConfig.set("EmuCore/GS", "pcrtc_antiblur", system.config["pcsx2_blur"])
    else:
        pcsx2INIConfig.set("EmuCore/GS", "pcrtc_antiblur", "true")
    # Integer Scaling
    if system.isOptSet("pcsx2_scaling"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "IntegerScaling", system.config["pcsx2_scaling"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "IntegerScaling", "false")
    # Blending Accuracy
    if system.isOptSet("pcsx2_blending"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "accurate_blending_unit", system.config["pcsx2_blending"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "accurate_blending_unit", "1")
    # Texture Filtering
    if system.isOptSet("pcsx2_texture_filtering"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "filter", system.config["pcsx2_texture_filtering"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "filter", "2")
    # Bilinear Filtering
    if system.isOptSet("pcsx2_bilinear_filtering"):
        pcsx2INIConfig.set(
            "EmuCore/GS",
            "linear_present_mode",
            system.config["pcsx2_bilinear_filtering"],
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "linear_present_mode", "1")
    # Load Texture Replacements
    if system.isOptSet("pcsx2_texture_replacements"):
        pcsx2INIConfig.set(
            "EmuCore/GS",
            "LoadTextureReplacements",
            system.config["pcsx2_texture_replacements"],
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "LoadTextureReplacements", "false")
    # OSD messages
    if system.isOptSet("pcsx2_osd_messages"):
        pcsx2INIConfig.set(
            "EmuCore/GS", "OsdShowMessages", system.config["pcsx2_osd_messages"]
        )
    else:
        pcsx2INIConfig.set("EmuCore/GS", "OsdShowMessages", "true")

    ## [InputSources]
    if not pcsx2INIConfig.has_section("InputSources"):
        pcsx2INIConfig.add_section("InputSources")

    pcsx2INIConfig.set("InputSources", "Keyboard", "true")
    pcsx2INIConfig.set("InputSources", "Mouse", "true")
    pcsx2INIConfig.set("InputSources", "SDL", "true")
    pcsx2INIConfig.set("InputSources", "SDLControllerEnhancedMode", "true")

    ## [Hotkeys]
    if not pcsx2INIConfig.has_section("Hotkeys"):
        pcsx2INIConfig.add_section("Hotkeys")

    pcsx2INIConfig.set("Hotkeys", "ToggleFullscreen", "Keyboard/Alt & Keyboard/Return")
    pcsx2INIConfig.set("Hotkeys", "CycleAspectRatio", "Keyboard/F6")
    pcsx2INIConfig.set("Hotkeys", "CycleInterlaceMode", "Keyboard/F5")
    pcsx2INIConfig.set("Hotkeys", "CycleMipmapMode", "Keyboard/Insert")
    pcsx2INIConfig.set(
        "Hotkeys", "GSDumpMultiFrame", "Keyboard/Control & Keyboard/Shift & Keyboard/F8"
    )
    pcsx2INIConfig.set("Hotkeys", "Screenshot", "Keyboard/F8")
    pcsx2INIConfig.set("Hotkeys", "GSDumpSingleFrame", "Keyboard/Shift & Keyboard/F8")
    pcsx2INIConfig.set("Hotkeys", "ToggleSoftwareRendering", "Keyboard/F9")
    pcsx2INIConfig.set("Hotkeys", "ZoomIn", "Keyboard/Control & Keyboard/Plus")
    pcsx2INIConfig.set("Hotkeys", "ZoomOut", "Keyboard/Control & Keyboard/Minus")
    pcsx2INIConfig.set("Hotkeys", "InputRecToggleMode", "Keyboard/Shift & Keyboard/R")
    pcsx2INIConfig.set("Hotkeys", "LoadStateFromSlot", "Keyboard/F3")
    pcsx2INIConfig.set("Hotkeys", "SaveStateToSlot", "Keyboard/F1")
    pcsx2INIConfig.set("Hotkeys", "NextSaveStateSlot", "Keyboard/F2")
    pcsx2INIConfig.set(
        "Hotkeys", "PreviousSaveStateSlot", "Keyboard/Shift & Keyboard/F2"
    )
    pcsx2INIConfig.set("Hotkeys", "OpenPauseMenu", "Keyboard/Escape")
    pcsx2INIConfig.set("Hotkeys", "ToggleFrameLimit", "Keyboard/F4")
    pcsx2INIConfig.set("Hotkeys", "TogglePause", "Keyboard/Space")
    pcsx2INIConfig.set(
        "Hotkeys", "ToggleSlowMotion", "Keyboard/Shift & Keyboard/Backtab"
    )
    pcsx2INIConfig.set("Hotkeys", "ToggleTurbo", "Keyboard/Tab")
    pcsx2INIConfig.set("Hotkeys", "HoldTurbo", "Keyboard/Period")

    # clean gun sections
    if (
        pcsx2INIConfig.has_section("USB1")
        and pcsx2INIConfig.has_option("USB1", "Type")
        and pcsx2INIConfig.get("USB1", "Type") == "guncon2"
    ):
        pcsx2INIConfig.remove_option("USB1", "Type")
    if (
        pcsx2INIConfig.has_section("USB2")
        and pcsx2INIConfig.has_option("USB2", "Type")
        and pcsx2INIConfig.get("USB2", "Type") == "guncon2"
    ):
        pcsx2INIConfig.remove_option("USB2", "Type")
    if pcsx2INIConfig.has_section("USB1") and pcsx2INIConfig.has_option(
        "USB1", "guncon2_Start"
    ):
        pcsx2INIConfig.remove_option("USB1", "guncon2_Start")
    if pcsx2INIConfig.has_section("USB2") and pcsx2INIConfig.has_option(
        "USB2", "guncon2_Start"
    ):
        pcsx2INIConfig.remove_option("USB2", "guncon2_Start")
    if pcsx2INIConfig.has_section("USB1") and pcsx2INIConfig.has_option(
        "USB1", "guncon2_C"
    ):
        pcsx2INIConfig.remove_option("USB1", "guncon2_C")
    if pcsx2INIConfig.has_section("USB2") and pcsx2INIConfig.has_option(
        "USB2", "guncon2_C"
    ):
        pcsx2INIConfig.remove_option("USB2", "guncon2_C")
    if pcsx2INIConfig.has_section("USB1") and pcsx2INIConfig.has_option(
        "USB1", "guncon2_numdevice"
    ):
        pcsx2INIConfig.remove_option("USB1", "guncon2_numdevice")
    if pcsx2INIConfig.has_section("USB2") and pcsx2INIConfig.has_option(
        "USB2", "guncon2_numdevice"
    ):
        pcsx2INIConfig.remove_option("USB2", "guncon2_numdevice")

    # clean wheel sections
    if (
        pcsx2INIConfig.has_section("USB1")
        and pcsx2INIConfig.has_option("USB1", "Type")
        and pcsx2INIConfig.get("USB1", "Type") == "Pad"
        and pcsx2INIConfig.has_option("USB1", "Pad_subtype")
        and pcsx2INIConfig.get("USB1", "Pad_subtype") == "1"
    ):
        pcsx2INIConfig.remove_option("USB1", "Type")
    if (
        pcsx2INIConfig.has_section("USB2")
        and pcsx2INIConfig.has_option("USB2", "Type")
        and pcsx2INIConfig.get("USB2", "Type") == "Pad"
        and pcsx2INIConfig.has_option("USB2", "Pad_subtype")
        and pcsx2INIConfig.get("USB2", "Pad_subtype") == "1"
    ):
        pcsx2INIConfig.remove_option("USB2", "Type")
    ###

    # guns
    if (
        system.isOptSet("use_guns")
        and system.getOptBoolean("use_guns")
        and len(guns) > 0
    ):
        gun1onport2 = (
            len(guns) == 1
            and "gun_gun1port" in metadata
            and metadata["gun_gun1port"] == "2"
        )
        pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}

        if len(guns) >= 1 and not gun1onport2:
            if not pcsx2INIConfig.has_section("USB1"):
                pcsx2INIConfig.add_section("USB1")
            pcsx2INIConfig.set("USB1", "Type", "guncon2")
            nc = 1
            for controller, pad in sorted(controllers.items()):
                if nc == 1 and not gun1onport2:
                    if "start" in pad.inputs:
                        pcsx2INIConfig.set(
                            "USB1",
                            "guncon2_Start",
                            "SDL-{}/{}".format(pad.index, "Start"),
                        )
                nc = nc + 1

            ### find a keyboard key to simulate the action of the player (always like button 2) ; search in system.conf, else default config
            if "controllers.pedals1" in system.config:
                pedalkey = system.config["controllers.pedals1"]
            else:
                pedalkey = pedalsKeys[1]
            pcsx2INIConfig.set("USB1", "guncon2_C", "Keyboard/" + pedalkey.upper())
            ###
        if len(guns) >= 2 or gun1onport2:
            if not pcsx2INIConfig.has_section("USB2"):
                pcsx2INIConfig.add_section("USB2")
            pcsx2INIConfig.set("USB2", "Type", "guncon2")
            nc = 1
            for controller, pad in sorted(controllers.items()):
                if nc == 2 or gun1onport2:
                    if "start" in pad.inputs:
                        pcsx2INIConfig.set(
                            "USB2",
                            "guncon2_Start",
                            "SDL-{}/{}".format(pad.index, "Start"),
                        )
                nc = nc + 1
            ### find a keyboard key to simulate the action of the player (always like button 2) ; search in system.conf, else default config
            if "controllers.pedals2" in system.config:
                pedalkey = system.config["controllers.pedals2"]
            else:
                pedalkey = pedalsKeys[2]
            pcsx2INIConfig.set("USB2", "guncon2_C", "Keyboard/" + pedalkey.upper())
            ###
            if gun1onport2:
                pcsx2INIConfig.set("USB2", "guncon2_numdevice", "0")
    # Gun crosshairs - one player only, PCSX2 can't distinguish both crosshair for some reason
    if pcsx2INIConfig.has_section("USB1"):
        if (
            system.isOptSet("pcsx2_crosshairs")
            and system.config["pcsx2_crosshairs"] == "1"
        ):
            pcsx2INIConfig.set(
                "USB1",
                "guncon2_cursor_path",
                "/usr/pcsx2/bin/resources/crosshairs/Blue.png",
            )
        else:
            pcsx2INIConfig.set("USB1", "guncon2_cursor_path", "")
    if pcsx2INIConfig.has_section("USB2"):
        if (
            system.isOptSet("pcsx2_crosshairs")
            and system.config["pcsx2_crosshairs"] == "1"
        ):
            pcsx2INIConfig.set(
                "USB2",
                "guncon2_cursor_path",
                "/usr/pcsx2/bin/resources/crosshairs/Red.png",
            )
        else:
            pcsx2INIConfig.set("USB2", "guncon2_cursor_path", "")
    # hack for the fog bug for guns (time crisis - crisis zone)
    fog_files = [
        "/usr/pcsx2/bin/resources/textures/SCES-52530/replacements/c321d53987f3986d-eadd4df7c9d76527-00005dd4.png",
        "/usr/pcsx2/bin/resources/textures/SLUS-20927/replacements/c321d53987f3986d-eadd4df7c9d76527-00005dd4.png",
    ]
    texture_dir = PCSX2_CONFIG_DIR + "/textures"
    # copy textures if necessary to PCSX2 config folder
    if (
        system.isOptSet("pcsx2_crisis_fog")
        and system.config["pcsx2_crisis_fog"] == "true"
    ):
        for file_path in fog_files:
            parent_directory_name = path.basename(path.dirname(path.dirname(file_path)))
            file_name = path.basename(file_path)
            texture_directory_path = path.join(
                texture_dir, parent_directory_name, "replacements"
            )
            makedirs(texture_directory_path, exist_ok=True)

            destination_file_path = path.join(texture_directory_path, file_name)

            copyfile(file_path, destination_file_path)
        # set texture replacement on regardless of previous setting
        pcsx2INIConfig.set("EmuCore/GS", "LoadTextureReplacements", "true")
    else:
        for file_path in fog_files:
            parent_directory_name = path.basename(path.dirname(path.dirname(file_path)))
            file_name = path.basename(file_path)
            texture_directory_path = path.join(
                texture_dir, parent_directory_name, "replacements"
            )
            target_file_path = path.join(texture_directory_path, file_name)

            if path.isfile(target_file_path):
                remove(target_file_path)

    # wheels
    wtype = getWheelType(metadata, playingWithWheel, system.config)
    eslog.info("PS2 wheel type is {}".format(wtype))
    if useEmulatorWheels(playingWithWheel, wtype):
        if len(wheels) >= 1:
            wheelMapping = {
                "DrivingForcePro": {
                    "up": "Pad_DPadUp",
                    "down": "Pad_DPadDown",
                    "left": "Pad_DPadLeft",
                    "right": "Pad_DPadRight",
                    "start": "Pad_Start",
                    "select": "Pad_Select",
                    "a": "Pad_Circle",
                    "b": "Pad_Cross",
                    "x": "Pad_Triangle",
                    "y": "Pad_Square",
                    "pageup": "Pad_L1",
                    "pagedown": "Pad_R1",
                },
                "DrivingForce": {
                    "up": "Pad_DPadUp",
                    "down": "Pad_DPadDown",
                    "left": "Pad_DPadLeft",
                    "right": "Pad_DPadRight",
                    "start": "Pad_Start",
                    "select": "Pad_Select",
                    "a": "Pad_Circle",
                    "b": "Pad_Cross",
                    "x": "Pad_Triangle",
                    "y": "Pad_Square",
                    "pageup": "Pad_L1",
                    "pagedown": "Pad_R1",
                },
                "GTForce": {
                    "a": "Pad_Y",
                    "b": "Pad_B",
                    "x": "Pad_X",
                    "y": "Pad_A",
                    "pageup": "Pad_MenuDown",
                    "pagedown": "Pad_MenuUp",
                },
            }

            usbx = 1
            for controller, pad in sorted(controllers.items()):
                if pad.dev in wheels:
                    if not pcsx2INIConfig.has_section("USB{}".format(usbx)):
                        pcsx2INIConfig.add_section("USB{}".format(usbx))
                    pcsx2INIConfig.set("USB{}".format(usbx), "Type", "Pad")

                    wheel_type = getWheelType(metadata, playingWithWheel, system.config)
                    pcsx2INIConfig.set(
                        "USB{}".format(usbx),
                        "Pad_subtype",
                        wheelTypeMapping[wheel_type],
                    )

                    if hasattr(pad, "physdev"):  # ffb on the real wheel
                        pcsx2INIConfig.set(
                            "USB{}".format(usbx),
                            "Pad_FFDevice",
                            "SDL-{}".format(pad.physid),
                        )
                    else:
                        pcsx2INIConfig.set(
                            "USB{}".format(usbx),
                            "Pad_FFDevice",
                            "SDL-{}".format(pad.index),
                        )

                    for i in pad.inputs:
                        if i in wheelMapping[wheel_type]:
                            pcsx2INIConfig.set(
                                "USB{}".format(usbx),
                                wheelMapping[wheel_type][i],
                                "SDL-{}/{}".format(
                                    pad.index, input2wheel(pad.inputs[i])
                                ),
                            )
                    # wheel
                    if "joystick1left" in pad.inputs:
                        pcsx2INIConfig.set(
                            "USB{}".format(usbx),
                            "Pad_SteeringLeft",
                            "SDL-{}/{}".format(
                                pad.index, input2wheel(pad.inputs["joystick1left"])
                            ),
                        )
                        pcsx2INIConfig.set(
                            "USB{}".format(usbx),
                            "Pad_SteeringRight",
                            "SDL-{}/{}".format(
                                pad.index,
                                input2wheel(pad.inputs["joystick1left"], True),
                            ),
                        )
                    # pedals
                    if "l2" in pad.inputs:
                        pcsx2INIConfig.set(
                            "USB{}".format(usbx),
                            "Pad_Brake",
                            "SDL-{}/{}".format(
                                pad.index, input2wheel(pad.inputs["l2"])
                            ),
                        )
                    if "r2" in pad.inputs:
                        pcsx2INIConfig.set(
                            "USB{}".format(usbx),
                            "Pad_Throttle",
                            "SDL-{}/{}".format(
                                pad.index, input2wheel(pad.inputs["r2"])
                            ),
                        )
                    usbx = usbx + 1

    ## [Pad]
    if not pcsx2INIConfig.has_section("Pad"):
        pcsx2INIConfig.add_section("Pad")

    pcsx2INIConfig.set("Pad", "MultitapPort1", "false")
    pcsx2INIConfig.set("Pad", "MultitapPort2", "false")

    # add multitap as needed
    multiTap = 2
    joystick_count = len(controllers)
    eslog.debug("Number of Controllers = {}".format(joystick_count))
    if system.isOptSet("pcsx2_multitap") and system.config["pcsx2_multitap"] == "4":
        if joystick_count > 2 and joystick_count < 5:
            pcsx2INIConfig.set("Pad", "MultitapPort1", "true")
            multiTap = int(system.config["pcsx2_multitap"])
        elif joystick_count > 4:
            pcsx2INIConfig.set("Pad", "MultitapPort1", "true")
            multiTap = 4
            eslog.debug(
                "*** You have too many connected controllers for this option, restricting to 4 ***"
            )
        else:
            multiTap = 2
            eslog.debug(
                "*** You have the wrong number of connected controllers for this option ***"
            )
    elif system.isOptSet("pcsx2_multitap") and system.config["pcsx2_multitap"] == "8":
        if joystick_count > 4:
            pcsx2INIConfig.set("Pad", "MultitapPort1", "true")
            pcsx2INIConfig.set("Pad", "MultitapPort2", "true")
            multiTap = int(system.config["pcsx2_multitap"])
        elif joystick_count > 2 and joystick_count < 5:
            pcsx2INIConfig.set("Pad", "MultitapPort1", "true")
            multiTap = 4
            eslog.debug(
                "*** You don't have enough connected controllers for this option, restricting to 4 ***"
            )
        else:
            multiTap = 2
            eslog.debug(
                "*** You don't have enough connected controllers for this option ***"
            )
    else:
        multiTap = 2

    # remove the previous [Padx] sections to avoid phantom controllers
    section_names = ["Pad1", "Pad2", "Pad3", "Pad4", "Pad5", "Pad6", "Pad7", "Pad8"]
    for section_name in section_names:
        if pcsx2INIConfig.has_section(section_name):
            pcsx2INIConfig.remove_section(section_name)

    # Now add Controllers
    nplayer = 1
    for controller, pad in sorted(controllers.items()):
        # only configure the number of controllers set
        if nplayer <= multiTap:
            pad_index = nplayer
            if multiTap == 4 and pad.index != 0:
                # Skip Pad2 in the ini file when MultitapPort1 only
                pad_index = nplayer + 1
            pad_num = "Pad{}".format(pad_index)
            sdl_num = "SDL-" + "{}".format(pad.index)

            if not pcsx2INIConfig.has_section(pad_num):
                pcsx2INIConfig.add_section(pad_num)

            pcsx2INIConfig.set(pad_num, "Type", "DualShock2")
            pcsx2INIConfig.set(pad_num, "InvertL", "0")
            pcsx2INIConfig.set(pad_num, "InvertR", "0")
            pcsx2INIConfig.set(pad_num, "Deadzone", "0")
            pcsx2INIConfig.set(pad_num, "AxisScale", "1.33")
            pcsx2INIConfig.set(pad_num, "TriggerDeadzone", "0")
            pcsx2INIConfig.set(pad_num, "TriggerScale", "1")
            pcsx2INIConfig.set(pad_num, "LargeMotorScale", "1")
            pcsx2INIConfig.set(pad_num, "SmallMotorScale", "1")
            pcsx2INIConfig.set(pad_num, "ButtonDeadzone", "0")
            pcsx2INIConfig.set(pad_num, "PressureModifier", "0.5")
            pcsx2INIConfig.set(pad_num, "Up", sdl_num + "/DPadUp")
            pcsx2INIConfig.set(pad_num, "Right", sdl_num + "/DPadRight")
            pcsx2INIConfig.set(pad_num, "Down", sdl_num + "/DPadDown")
            pcsx2INIConfig.set(pad_num, "Left", sdl_num + "/DPadLeft")
            pcsx2INIConfig.set(pad_num, "Triangle", sdl_num + "/Y")
            pcsx2INIConfig.set(pad_num, "Circle", sdl_num + "/B")
            pcsx2INIConfig.set(pad_num, "Cross", sdl_num + "/A")
            pcsx2INIConfig.set(pad_num, "Square", sdl_num + "/X")
            pcsx2INIConfig.set(pad_num, "Select", sdl_num + "/Back")
            pcsx2INIConfig.set(pad_num, "Start", sdl_num + "/Start")
            pcsx2INIConfig.set(pad_num, "L1", sdl_num + "/LeftShoulder")
            pcsx2INIConfig.set(pad_num, "L2", sdl_num + "/+LeftTrigger")
            pcsx2INIConfig.set(pad_num, "R1", sdl_num + "/RightShoulder")
            pcsx2INIConfig.set(pad_num, "R2", sdl_num + "/+RightTrigger")
            pcsx2INIConfig.set(pad_num, "L3", sdl_num + "/LeftStick")
            pcsx2INIConfig.set(pad_num, "R3", sdl_num + "/RightStick")
            pcsx2INIConfig.set(pad_num, "LUp", sdl_num + "/-LeftY")
            pcsx2INIConfig.set(pad_num, "LRight", sdl_num + "/+LeftX")
            pcsx2INIConfig.set(pad_num, "LDown", sdl_num + "/+LeftY")
            pcsx2INIConfig.set(pad_num, "LLeft", sdl_num + "/-LeftX")
            pcsx2INIConfig.set(pad_num, "RUp", sdl_num + "/-RightY")
            pcsx2INIConfig.set(pad_num, "RRight", sdl_num + "/+RightX")
            pcsx2INIConfig.set(pad_num, "RDown", sdl_num + "/+RightY")
            pcsx2INIConfig.set(pad_num, "RLeft", sdl_num + "/-RightX")
            pcsx2INIConfig.set(pad_num, "Analog", sdl_num + "/Guide")
            pcsx2INIConfig.set(pad_num, "LargeMotor", sdl_num + "/LargeMotor")
            pcsx2INIConfig.set(pad_num, "SmallMotor", sdl_num + "/SmallMotor")

        nplayer += 1

    ## [GameList]
    if not pcsx2INIConfig.has_section("GameList"):
        pcsx2INIConfig.add_section("GameList")

    pcsx2INIConfig.set("GameList", "RecursivePaths", "/userdata/roms/ps2")

    with open(configFileName, "w") as configfile:
        pcsx2INIConfig.write(configfile)
