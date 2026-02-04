from configparser import ConfigParser
from pathlib import Path
from shutil import copyfile
from subprocess import CalledProcessError, check_output
from time import time
from typing import Any

from requests import get

from configgen.systemFiles import BIOS, CONF
from configgen.utils.logger import get_logger

from .pcsx2Controllers import (
    getWheelType,
    input2wheel,
    useEmulatorWheels,
    wheelTypeMapping,
)

PCSX2_CONFIG_DIR = CONF / "PCSX2"
PCSX2_BIOS_DIR = BIOS / "ps2"
PCSX2_BIN_PATH = Path("/usr/pcsx2/bin/pcsx2-qt")
PCSX2_PATCHES_PATH = PCSX2_BIOS_DIR / "patches.zip"
PCSX2_SOURCE_PATH = Path("/usr/share/reglinux/datainit/bios/ps2/patches.zip")


eslog = get_logger(__name__)


def setPcsx2Reg():
    configFileName = PCSX2_CONFIG_DIR / "PCSX2-reg.ini"
    if not PCSX2_CONFIG_DIR.exists():
        PCSX2_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with Path(configFileName).open("w") as f:
        f.write("DocumentsFolderMode=User\n")
        f.write("CustomDocumentsFolder=/usr/pcsx2/bin\n")
        f.write("UseDefaultSettingsFolder=enabled\n")
        f.write("SettingsFolder=/userdata/system/configs/PCSX2/inis\n")
        f.write("Install_Dir=/usr/pcsx2/bin\n")
        f.write("RunWizard=0\n")
        f.close()


def configureAudio():
    config_dir = PCSX2_CONFIG_DIR / "inis"
    configFileName = config_dir / "spu2-x.ini"
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

    # Keep the custom files
    if configFileName.exists():
        return

    with Path(configFileName).open("w") as f:
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


# Helper function to set configuration options with default values
def set_option_with_default(
    config: ConfigParser,
    system: Any,
    section: str,
    option: str,
    config_key: str,
    default_value: str = "false",
) -> None:
    """Set a configuration option with a default value if the option is not set in the system configuration.

    Args:
        config: The configuration object to set the option on
        system: The system configuration object
        section: The section name in the configuration file
        option: The option name to set
        config_key: The key in the system configuration to check
        default_value: The default value to use if the option is not set (default: "false")

    """
    if system.isOptSet(config_key):
        value = system.config[config_key]
        # For fastboot, we invert the logic (0 disables, 1 enables)
        if config_key == "pcsx2_fastboot":
            config.set(section, option, "true" if value != "0" else "false")
        else:
            config.set(section, option, value)
    else:
        config.set(section, option, default_value)


# Helper function to set boolean configuration options
def set_boolean_option(
    config: ConfigParser,
    section: str,
    option: str,
    value: str,
) -> None:
    """Set a boolean configuration option based on the input value.

    Args:
        config: The configuration object to set the option on
        section: The section name in the configuration file
        option: The option name to set
        value: The value to convert to boolean ("1" becomes "true", anything else becomes "false")

    """
    config.set(section, option, "true" if value == "1" else "false")


def setPcsx2Config(
    system: Any,
    rom: str,
    controllers: Any,
    metadata: Any,
    guns: Any,
    wheels: Any,
    playingWithWheel: Any,
) -> None:
    """Configure PCSX2 emulator settings based on system configuration.

    Args:
        system: System configuration object containing settings
        rom: Path to the ROM file being loaded
        controllers: Controller configuration data
        metadata: Metadata about the game
        guns: Gun configuration data
        wheels: Wheel configuration data
        playingWithWheel: Boolean indicating if playing with wheel

    """
    config_dir = PCSX2_CONFIG_DIR / "inis"
    configFileName = config_dir / "PCSX2.ini"

    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

    if not configFileName.is_file():
        Path(configFileName).write_text("[UI]\n")

    pcsx2INIConfig = ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    pcsx2INIConfig.optionxform = lambda optionstr: str(optionstr)

    if configFileName.is_file():
        pcsx2INIConfig.read(configFileName)

    # [UI]
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

    # [Folders]
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
    cache_dir = Path("/userdata/system/cache/ps2")
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)

    # [EmuCore]
    if not pcsx2INIConfig.has_section("EmuCore"):
        pcsx2INIConfig.add_section("EmuCore")

    # set the settings we want always enabled
    pcsx2INIConfig.set("EmuCore", "EnableDiscordPresence", "false")

    # Fastboot
    if system.isOptSet("pcsx2_fastboot"):
        pcsx2INIConfig.set(
            "EmuCore",
            "EnableFastBoot",
            "true" if system.config["pcsx2_fastboot"] != "0" else "false",
        )
    else:
        pcsx2INIConfig.set("EmuCore", "EnableFastBoot", "false")

    # Outras configurações
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore",
        "EnableCheats",
        "pcsx2_cheats",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore",
        "EnableWideScreenPatches",
        "pcsx2_EnableWideScreenPatches",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore",
        "EnableNoInterlacingPatches",
        "pcsx2_interlacing_patches",
    )

    # [Achievements]
    if not pcsx2INIConfig.has_section("Achievements"):
        pcsx2INIConfig.add_section("Achievements")
    pcsx2INIConfig.set("Achievements", "Enabled", "false")

    # Helper function to set boolean configuration options
    def set_boolean_option(section: str, option: str, value: str) -> None:
        pcsx2INIConfig.set(section, option, "true" if value == "1" else "false")

    if system.isOptSet("retroachievements") and system.getOptBoolean(
        "retroachievements",
    ):
        username = system.config.get("retroachievements.username", "")
        hardcore = system.config.get("retroachievements.hardcore", "")
        indicator = system.config.get("retroachievements.challenge_indicators", "")
        presence = system.config.get("retroachievements.richpresence", "")
        leaderbd = system.config.get("retroachievements.leaderboards", "")
        password = system.config.get("retroachievements.password", "")
        login_cmd = f"dorequest.php?r=login&u={username}&p={password}"
        try:
            res = get(
                "https://retroachievements.org/" + login_cmd,
                headers={"Content-type": "text/plain", "User-Agent": "REG-linux"},
            )
            if res.status_code != 200:
                eslog.warning(
                    f"ERROR: RetroAchievements.org responded with #{res.status_code} [{res.reason}]",
                )
                pcsx2INIConfig.set("Achievements", "Enabled", "false")
            else:
                res.encoding = "utf-8"
                parsedout = res.json()
                if not parsedout["Success"]:
                    eslog.warning(
                        f"ERROR: RetroAchievements login failed with ({parsedout!s})",
                    )
                token = parsedout["Token"]
                pcsx2INIConfig.set("Achievements", "Enabled", "true")
                pcsx2INIConfig.set("Achievements", "Username", username)
                pcsx2INIConfig.set("Achievements", "Token", token)
                pcsx2INIConfig.set("Achievements", "LoginTimestamp", str(int(time())))

                # Using the helper function to set boolean options
                set_boolean_option("Achievements", "ChallengeMode", hardcore)
                set_boolean_option("Achievements", "PrimedIndicators", indicator)
                set_boolean_option("Achievements", "RichPresence", presence)
                set_boolean_option("Achievements", "Leaderboards", leaderbd)
        except (Exception, ValueError) as e:
            eslog.error(f"ERROR: setting RetroAchievements parameters - {e!s}")

    # set other settings
    pcsx2INIConfig.set("Achievements", "TestMode", "false")
    pcsx2INIConfig.set("Achievements", "UnofficialTestMode", "false")
    pcsx2INIConfig.set("Achievements", "Notifications", "true")
    pcsx2INIConfig.set("Achievements", "SoundEffects", "true")

    # [Filenames]
    if not pcsx2INIConfig.has_section("Filenames"):
        pcsx2INIConfig.add_section("Filenames")

    # [EMUCORE/GS]
    if not pcsx2INIConfig.has_section("EmuCore/GS"):
        pcsx2INIConfig.add_section("EmuCore/GS")

    # Renderer
    # Check Vulkan first to be sure
    try:
        have_vulkan = check_output(
            ["/usr/bin/system-vulkan", "hasVulkan"],
            text=True,
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
                            ["/usr/bin/system-vulkan", "hasDiscrete"],
                            text=True,
                        ).strip()
                        if have_discrete == "true":
                            eslog.debug(
                                "A discrete GPU is available on the system. We will use that for performance",
                            )
                            try:
                                discrete_name = check_output(
                                    ["/usr/bin/system-vulkan", "discreteName"],
                                    text=True,
                                ).strip()
                                if discrete_name:
                                    eslog.debug(
                                        f"Using Discrete GPU Name: {discrete_name} for PCSX2",
                                    )
                                    pcsx2INIConfig.set(
                                        "EmuCore/GS",
                                        "Adapter",
                                        discrete_name,
                                    )
                                else:
                                    eslog.debug("Couldn't get discrete GPU Name")
                                    pcsx2INIConfig.set(
                                        "EmuCore/GS",
                                        "Adapter",
                                        "(Default)",
                                    )
                            except CalledProcessError as e:
                                eslog.debug(f"Error getting discrete GPU Name: {e}")
                                pcsx2INIConfig.set("EmuCore/GS", "Adapter", "(Default)")
                        else:
                            eslog.debug(
                                "Discrete GPU is not available on the system. Using default.",
                            )
                            pcsx2INIConfig.set("EmuCore/GS", "Adapter", "(Default)")
                    except CalledProcessError as e:
                        eslog.debug(f"Error checking for discrete GPU: {e}")
            else:
                eslog.debug("User selected or defaulting to OpenGL")

            pcsx2INIConfig.set("EmuCore/GS", "Renderer", renderer)
        else:
            eslog.debug(
                "Vulkan driver is not available on the system. Falling back to OpenGL",
            )
            pcsx2INIConfig.set("EmuCore/GS", "Renderer", "12")
    except CalledProcessError as e:
        eslog.debug(f"Error checking for Vulkan driver: {e}")

    # Configurações de vídeo
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "AspectRatio",
        "pcsx2_ratio",
        "Auto 4:3/3:2",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "VsyncEnable",
        "pcsx2_vsync",
        "0",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "upscale_multiplier",
        "pcsx2_resolution",
        "1",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "fxaa",
        "pcsx2_fxaa",
        "false",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "FMVAspectRatioSwitch",
        "pcsx2_fmv_ratio",
        "Auto 4:3/3:2",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "mipmap_hw",
        "pcsx2_mipmapping",
        "-1",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "TriFilter",
        "pcsx2_trilinear_filtering",
        "-1",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "MaxAnisotropy",
        "pcsx2_anisotropic_filtering",
        "0",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "dithering_ps2",
        "pcsx2_dithering",
        "2",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "texture_preloading",
        "pcsx2_texture_loading",
        "2",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "deinterlace_mode",
        "pcsx2_deinterlacing",
        "0",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "pcrtc_antiblur",
        "pcsx2_blur",
        "true",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "IntegerScaling",
        "pcsx2_scaling",
        "false",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "accurate_blending_unit",
        "pcsx2_blending",
        "1",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "filter",
        "pcsx2_texture_filtering",
        "2",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "linear_present_mode",
        "pcsx2_bilinear_filtering",
        "1",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "LoadTextureReplacements",
        "pcsx2_texture_replacements",
        "false",
    )
    set_option_with_default(
        pcsx2INIConfig,
        system,
        "EmuCore/GS",
        "OsdShowMessages",
        "pcsx2_osd_messages",
        "true",
    )

    # [InputSources]
    if not pcsx2INIConfig.has_section("InputSources"):
        pcsx2INIConfig.add_section("InputSources")

    # Define input sources
    input_sources = {
        "Keyboard": "true",
        "Mouse": "true",
        "SDL": "true",
        "SDLControllerEnhancedMode": "true",
    }

    for source, value in input_sources.items():
        pcsx2INIConfig.set("InputSources", source, value)

    # [Hotkeys]
    if not pcsx2INIConfig.has_section("Hotkeys"):
        pcsx2INIConfig.add_section("Hotkeys")

    # Define keyboard shortcuts
    hotkeys = {
        "ToggleFullscreen": "Keyboard/Alt & Keyboard/Return",
        "CycleAspectRatio": "Keyboard/F6",
        "CycleInterlaceMode": "Keyboard/F5",
        "CycleMipmapMode": "Keyboard/Insert",
        "GSDumpMultiFrame": "Keyboard/Control & Keyboard/Shift & Keyboard/F8",
        "Screenshot": "Keyboard/F8",
        "GSDumpSingleFrame": "Keyboard/Shift & Keyboard/F8",
        "ToggleSoftwareRendering": "Keyboard/F9",
        "ZoomIn": "Keyboard/Control & Keyboard/Plus",
        "ZoomOut": "Keyboard/Control & Keyboard/Minus",
        "InputRecToggleMode": "Keyboard/Shift & Keyboard/R",
        "LoadStateFromSlot": "Keyboard/F3",
        "SaveStateToSlot": "Keyboard/F1",
        "NextSaveStateSlot": "Keyboard/F2",
        "PreviousSaveStateSlot": "Keyboard/Shift & Keyboard/F2",
        "OpenPauseMenu": "Keyboard/Escape",
        "ToggleFrameLimit": "Keyboard/F4",
        "TogglePause": "Keyboard/Space",
        "ToggleSlowMotion": "Keyboard/Shift & Keyboard/Backtab",
        "ToggleTurbo": "Keyboard/Tab",
        "HoldTurbo": "Keyboard/Period",
    }

    for hotkey, value in hotkeys.items():
        pcsx2INIConfig.set("Hotkeys", hotkey, value)

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
        "USB1",
        "guncon2_Start",
    ):
        pcsx2INIConfig.remove_option("USB1", "guncon2_Start")
    if pcsx2INIConfig.has_section("USB2") and pcsx2INIConfig.has_option(
        "USB2",
        "guncon2_Start",
    ):
        pcsx2INIConfig.remove_option("USB2", "guncon2_Start")
    if pcsx2INIConfig.has_section("USB1") and pcsx2INIConfig.has_option(
        "USB1",
        "guncon2_C",
    ):
        pcsx2INIConfig.remove_option("USB1", "guncon2_C")
    if pcsx2INIConfig.has_section("USB2") and pcsx2INIConfig.has_option(
        "USB2",
        "guncon2_C",
    ):
        pcsx2INIConfig.remove_option("USB2", "guncon2_C")
    if pcsx2INIConfig.has_section("USB1") and pcsx2INIConfig.has_option(
        "USB1",
        "guncon2_numdevice",
    ):
        pcsx2INIConfig.remove_option("USB1", "guncon2_numdevice")
    if pcsx2INIConfig.has_section("USB2") and pcsx2INIConfig.has_option(
        "USB2",
        "guncon2_numdevice",
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
            for _, pad in sorted(controllers.items()):
                if nc == 1 and not gun1onport2 and "start" in pad.inputs:
                    pcsx2INIConfig.set(
                        "USB1",
                        "guncon2_Start",
                        f"SDL-{pad.index}/Start",
                    )
                nc = nc + 1

            # find a keyboard key to simulate the action of the player (always like button 2) ; search in system.conf, else default config
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
            for _, pad in sorted(controllers.items()):
                if (nc == 2 or gun1onport2) and "start" in pad.inputs:
                    pcsx2INIConfig.set(
                        "USB2",
                        "guncon2_Start",
                        f"SDL-{pad.index}/Start",
                    )
                nc = nc + 1
            # find a keyboard key to simulate the action of the player (always like button 2) ; search in system.conf, else default config
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
    texture_dir = str(Path(PCSX2_CONFIG_DIR) / "textures")
    # copy textures if necessary to PCSX2 config folder
    if (
        system.isOptSet("pcsx2_crisis_fog")
        and system.config["pcsx2_crisis_fog"] == "true"
    ):
        for file_path in fog_files:
            file_path_obj = Path(file_path)
            parent_directory_name = file_path_obj.parent.parent.name
            file_name = file_path_obj.name
            texture_directory_path = (
                Path(texture_dir) / parent_directory_name / "replacements"
            )
            texture_directory_path.mkdir(parents=True, exist_ok=True)

            destination_file_path = texture_directory_path / file_name

            copyfile(str(file_path_obj), str(destination_file_path))
        # set texture replacement on regardless of previous setting
        pcsx2INIConfig.set("EmuCore/GS", "LoadTextureReplacements", "true")
    else:
        for file_path in fog_files:
            file_path_obj = Path(file_path)
            parent_directory_name = file_path_obj.parent.parent.name
            file_name = file_path_obj.name
            texture_directory_path = (
                Path(texture_dir) / parent_directory_name / "replacements"
            )
            target_file_path = texture_directory_path / file_name

            if target_file_path.is_file():
                target_file_path.unlink()

    # wheels
    wtype = getWheelType(metadata, playingWithWheel, system.config)
    eslog.info(f"PS2 wheel type is {wtype}")
    if useEmulatorWheels(playingWithWheel, wtype) and len(wheels) >= 1:
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
        for _, pad in sorted(controllers.items()):
            if pad.dev in wheels:
                if not pcsx2INIConfig.has_section(f"USB{usbx}"):
                    pcsx2INIConfig.add_section(f"USB{usbx}")
                pcsx2INIConfig.set(f"USB{usbx}", "Type", "Pad")

                wheel_type = getWheelType(metadata, playingWithWheel, system.config)
                pcsx2INIConfig.set(
                    f"USB{usbx}",
                    "Pad_subtype",
                    wheelTypeMapping[wheel_type],
                )

                if hasattr(pad, "physdev"):  # ffb on the real wheel
                    pcsx2INIConfig.set(
                        f"USB{usbx}",
                        "Pad_FFDevice",
                        f"SDL-{pad.physid}",
                    )
                else:
                    pcsx2INIConfig.set(
                        f"USB{usbx}",
                        "Pad_FFDevice",
                        f"SDL-{pad.index}",
                    )

                for i in pad.inputs:
                    if i in wheelMapping[wheel_type]:
                        pcsx2INIConfig.set(
                            f"USB{usbx}",
                            wheelMapping[wheel_type][i],
                            f"SDL-{pad.index}/{input2wheel(pad.inputs[i])}",
                        )
                # wheel
                if "joystick1left" in pad.inputs:
                    pcsx2INIConfig.set(
                        f"USB{usbx}",
                        "Pad_SteeringLeft",
                        f"SDL-{pad.index}/{input2wheel(pad.inputs['joystick1left'])}",
                    )
                    pcsx2INIConfig.set(
                        f"USB{usbx}",
                        "Pad_SteeringRight",
                        f"SDL-{pad.index}/{input2wheel(pad.inputs['joystick1left'], True)}",
                    )
                # pedals
                if "l2" in pad.inputs:
                    pcsx2INIConfig.set(
                        f"USB{usbx}",
                        "Pad_Brake",
                        f"SDL-{pad.index}/{input2wheel(pad.inputs['l2'])}",
                    )
                if "r2" in pad.inputs:
                    pcsx2INIConfig.set(
                        f"USB{usbx}",
                        "Pad_Throttle",
                        f"SDL-{pad.index}/{input2wheel(pad.inputs['r2'])}",
                    )
                usbx = usbx + 1

    # [Pad]
    if not pcsx2INIConfig.has_section("Pad"):
        pcsx2INIConfig.add_section("Pad")

    # Define multitap settings
    pcsx2INIConfig.set("Pad", "MultitapPort1", "false")
    pcsx2INIConfig.set("Pad", "MultitapPort2", "false")

    # Function to determine the number of multitaps
    def get_multitap_config(
        system: Any,
        controllers: Any,
    ) -> tuple[int, dict[str, str]]:
        multiTap = 2
        multitap_settings = {"MultitapPort1": "false", "MultitapPort2": "false"}
        joystick_count = len(controllers)
        eslog.debug(f"Number of Controllers = {joystick_count}")

        if system.isOptSet("pcsx2_multitap") and system.config["pcsx2_multitap"] == "4":
            if joystick_count > 2 and joystick_count < 5:
                multitap_settings["MultitapPort1"] = "true"
                multiTap = 4
            elif joystick_count > 4:
                multitap_settings["MultitapPort1"] = "true"
                multiTap = 4
                eslog.debug(
                    "*** You have too many connected controllers for this option, restricting to 4 ***",
                )
            else:
                multiTap = 2
                eslog.debug(
                    "*** You have the wrong number of connected controllers for this option ***",
                )
        elif (
            system.isOptSet("pcsx2_multitap") and system.config["pcsx2_multitap"] == "8"
        ):
            if joystick_count > 4:
                multitap_settings["MultitapPort1"] = "true"
                multitap_settings["MultitapPort2"] = "true"
                multiTap = 8
            elif joystick_count > 2 and joystick_count < 5:
                multitap_settings["MultitapPort1"] = "true"
                multiTap = 4
                eslog.debug(
                    "*** You don't have enough connected controllers for this option, restricting to 4 ***",
                )
            else:
                multiTap = 2
                eslog.debug(
                    "*** You don't have enough connected controllers for this option ***",
                )

        return multiTap, multitap_settings

    # Apply multitap settings
    multiTap, multitap_settings = get_multitap_config(system, controllers)
    for setting, value in multitap_settings.items():
        pcsx2INIConfig.set("Pad", setting, value)

    # remove the previous [Padx] sections to avoid phantom controllers
    section_names = ["Pad1", "Pad2", "Pad3", "Pad4", "Pad5", "Pad6", "Pad7", "Pad8"]
    for section_name in section_names:
        if pcsx2INIConfig.has_section(section_name):
            pcsx2INIConfig.remove_section(section_name)

    # Default controller settings
    controller_defaults = {
        "Type": "DualShock2",
        "InvertL": "0",
        "InvertR": "0",
        "Deadzone": "0",
        "AxisScale": "1.33",
        "TriggerDeadzone": "0",
        "TriggerScale": "1",
        "LargeMotorScale": "1",
        "SmallMotorScale": "1",
        "ButtonDeadzone": "0",
        "PressureModifier": "0.5",
    }

    # Button mapping
    button_mapping = {
        "Up": "DPadUp",
        "Right": "DPadRight",
        "Down": "DPadDown",
        "Left": "DPadLeft",
        "Triangle": "Y",
        "Circle": "B",
        "Cross": "A",
        "Square": "X",
        "Select": "Back",
        "Start": "Start",
        "L1": "LeftShoulder",
        "L2": "+LeftTrigger",
        "R1": "RightShoulder",
        "R2": "+RightTrigger",
        "L3": "LeftStick",
        "R3": "RightStick",
        "LUp": "-LeftY",
        "LRight": "+LeftX",
        "LDown": "+LeftY",
        "LLeft": "-LeftX",
        "RUp": "-RightY",
        "RRight": "+RightX",
        "RDown": "+RightY",
        "RLeft": "-RightX",
        "Analog": "Guide",
        "LargeMotor": "LargeMotor",
        "SmallMotor": "SmallMotor",
    }

    # Now add Controllers
    for nplayer, pad in enumerate(sorted(controllers.items()), start=1):
        # only configure the number of controllers set
        if nplayer <= multiTap:
            pad_index = nplayer
            if multiTap == 4 and pad.index != 0:
                # Skip Pad2 in the ini file when MultitapPort1 only
                pad_index = nplayer + 1
            pad_num = f"Pad{pad_index}"
            sdl_num = f"SDL-{pad.index}"

            if not pcsx2INIConfig.has_section(pad_num):
                pcsx2INIConfig.add_section(pad_num)

            # Apply default settings
            for setting, value in controller_defaults.items():
                pcsx2INIConfig.set(pad_num, setting, value)

            # Apply button mapping
            for button, input_name in button_mapping.items():
                pcsx2INIConfig.set(pad_num, button, f"{sdl_num}/{input_name}")

    # [GameList]
    if not pcsx2INIConfig.has_section("GameList"):
        pcsx2INIConfig.add_section("GameList")

    pcsx2INIConfig.set("GameList", "RecursivePaths", str(Path("/userdata/roms/ps2")))

    with Path(configFileName).open("w") as configfile:
        pcsx2INIConfig.write(configfile)


def getGfxRatioFromConfig(config: Any, gameResolution: dict[str, int]) -> str:
    """Map configuration ratio values to the values used by the ratio calculation function.

    Args:
        config: Configuration object containing settings
        gameResolution: Dictionary containing game resolution (width, height)

    Returns:
        str: The ratio value mapped from the configuration

    """
    # Mapping of configuration values to ratio values used in the function
    if "pcsx2_ratio" in config:
        ratio_value = config["pcsx2_ratio"]
        if ratio_value in ["16:9", "16/9"]:
            return "16:9"
        if ratio_value in ["full", "stretch", "Stretch"]:
            return "Stretch"
        if ratio_value in ["4:3", "4/3"]:
            return "4:3"
        if ratio_value in ["16:10", "16/10"]:
            return "16:10"
        # Add other values as needed
    return "4:3"  # Default value


def getInGameRatio(config: Any, gameResolution: dict[str, int], rom: str) -> float:
    """Calculate the in-game aspect ratio based on configuration and game resolution.

    Args:
        config: Configuration object containing settings
        gameResolution: Dictionary containing game resolution (width, height)
        rom: Path to the ROM file being loaded

    Returns:
        float: The calculated aspect ratio as a fraction (e.g., 4/3, 16/9)

    """
    ratio_from_config = getGfxRatioFromConfig(config, gameResolution)
    if (
        ratio_from_config == "16:9"
        or ratio_from_config == "16:10"
        or (
            ratio_from_config == "Stretch"
            and gameResolution["width"] / float(gameResolution["height"])
            > ((16.0 / 9.0) - 0.1)
        )
    ):
        return 16 / 9
    return 4 / 3
