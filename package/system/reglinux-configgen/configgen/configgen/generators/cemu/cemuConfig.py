from os import environ
from subprocess import PIPE, CalledProcessError, check_output, run
from typing import Any

from configgen.systemFiles import BIOS, CONF, ROMS, SAVES
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

CEMU_CONFIG_DIR = CONF + "/cemu"
CEMU_CONFIG_PATH = CEMU_CONFIG_DIR + "/settings.xml"
CEMU_BIOS_DIR = BIOS + "/cemu"
CEMU_PROFILES_DIR = CEMU_CONFIG_DIR + "/controllerProfiles"
CEMU_ROMS_DIR = ROMS + "/wiiu"
CEMU_SAVES_DIR = SAVES + "/wiiu"
CEMU_BIN_PATH = "/usr/bin/cemu/cemu"


def setCemuConfig(cemuConfig: Any, system: Any) -> None:
    # [ROOT]
    xml_root = getRoot(cemuConfig, "content")
    # Default mlc path
    setSectionConfig(cemuConfig, xml_root, "mlc_path", CEMU_SAVES_DIR)
    # Remove auto updates
    setSectionConfig(cemuConfig, xml_root, "check_update", "false")
    # Avoid the welcome window
    setSectionConfig(cemuConfig, xml_root, "gp_download", "true")
    # Other options
    setSectionConfig(cemuConfig, xml_root, "logflag", "0")
    setSectionConfig(cemuConfig, xml_root, "advanced_ppc_logging", "false")
    setSectionConfig(cemuConfig, xml_root, "use_discord_presence", "false")
    setSectionConfig(cemuConfig, xml_root, "fullscreen_menubar", "false")
    setSectionConfig(cemuConfig, xml_root, "vk_warning", "false")
    setSectionConfig(cemuConfig, xml_root, "fullscreen", "true")
    # Language
    if (
        not system.isOptSet("cemu_console_language")
        or system.config["cemu_console_language"] == "ui"
    ):
        lang = getLangFromEnvironment()
    else:
        lang = system.config["cemu_console_language"]
    setSectionConfig(cemuConfig, xml_root, "console_language", str(getCemuLang(lang)))

    # [WINDOWS]
    # Position
    setSectionConfig(cemuConfig, xml_root, "window_position", "")
    window_position = getRoot(cemuConfig, "window_position")
    setSectionConfig(cemuConfig, window_position, "x", "0")
    setSectionConfig(cemuConfig, window_position, "y", "0")
    # Size
    setSectionConfig(cemuConfig, xml_root, "window_size", "")
    window_size = getRoot(cemuConfig, "window_size")
    setSectionConfig(cemuConfig, window_size, "x", "640")
    setSectionConfig(cemuConfig, window_size, "y", "480")

    # [GAMEPAD]
    if system.isOptSet("cemu_gamepad") and system.config["cemu_gamepad"] == "True":
        setSectionConfig(cemuConfig, xml_root, "open_pad", "true")
    else:
        setSectionConfig(cemuConfig, xml_root, "open_pad", "false")
    setSectionConfig(cemuConfig, xml_root, "pad_position", "")
    pad_position = getRoot(cemuConfig, "pad_position")
    setSectionConfig(cemuConfig, pad_position, "x", "0")
    setSectionConfig(cemuConfig, pad_position, "y", "0")
    # Size
    setSectionConfig(cemuConfig, xml_root, "pad_size", "")
    pad_size = getRoot(cemuConfig, "pad_size")
    setSectionConfig(cemuConfig, pad_size, "x", "640")
    setSectionConfig(cemuConfig, pad_size, "y", "480")

    # [GAME PATH]
    setSectionConfig(cemuConfig, xml_root, "GamePaths", "")
    game_root = getRoot(cemuConfig, "GamePaths")
    # Default games path
    setSectionConfig(cemuConfig, game_root, "Entry", CEMU_ROMS_DIR)

    # [GRAPHICS]
    setSectionConfig(cemuConfig, xml_root, "Graphic", "")
    graphic_root = getRoot(cemuConfig, "Graphic")
    # Graphical backend
    if system.isOptSet("cemu_gfxbackend"):
        api_value = system.config["cemu_gfxbackend"]
    else:
        api_value = "1"  # Vulkan
    setSectionConfig(cemuConfig, graphic_root, "api", api_value)
    # Only set the graphics `device` if Vulkan
    if api_value == "1":
        # Check if we have a discrete GPU & if so, set the UUID
        try:
            have_vulkan = check_output(
                ["/usr/bin/system-vulkan", "hasVulkan"], text=True
            ).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    have_discrete = check_output(
                        ["/usr/bin/system-vulkan", "hasDiscrete"], text=True
                    ).strip()
                    if have_discrete == "true":
                        eslog.debug(
                            "A discrete GPU is available on the system. We will use that for performance"
                        )
                        try:
                            discrete_uuid = check_output(
                                ["/usr/bin/system-vulkan", "discreteUUID"], text=True
                            ).strip()
                            if discrete_uuid != "":
                                discrete_uuid_num = discrete_uuid.replace("-", "")
                                eslog.debug(
                                    f"Using Discrete GPU UUID: {discrete_uuid_num} for Cemu"
                                )
                                setSectionConfig(
                                    cemuConfig,
                                    graphic_root,
                                    "device",
                                    discrete_uuid_num,
                                )
                            else:
                                eslog.debug("Couldn't get discrete GPU UUID!")
                        except CalledProcessError:
                            eslog.debug("Error getting discrete GPU UUID!")
                    else:
                        eslog.debug(
                            "Discrete GPU is not available on the system. Using default."
                        )
                except CalledProcessError:
                    eslog.debug("Error checking for discrete GPU.")
            else:
                eslog.debug(
                    "Vulkan driver is not available on the system. Falling back to OpenGL"
                )
                setSectionConfig(cemuConfig, graphic_root, "api", "0")
        except CalledProcessError:
            eslog.debug("Error executing system-vulkan script.")

    # Async VULKAN Shader compilation
    if system.isOptSet("cemu_async") and system.config["cemu_async"] == "False":
        setSectionConfig(cemuConfig, graphic_root, "AsyncCompile", "false")
    else:
        setSectionConfig(cemuConfig, graphic_root, "AsyncCompile", "true")
    # Vsync
    if system.isOptSet("cemu_vsync"):
        setSectionConfig(cemuConfig, graphic_root, "VSync", system.config["cemu_vsync"])
    else:
        setSectionConfig(cemuConfig, graphic_root, "VSync", "0")  # Off
    # Upscale Filter
    if system.isOptSet("cemu_upscale"):
        setSectionConfig(
            cemuConfig, graphic_root, "UpscaleFilter", system.config["cemu_upscale"]
        )
    else:
        setSectionConfig(cemuConfig, graphic_root, "UpscaleFilter", "2")  # Hermite
    # Downscale Filter
    if system.isOptSet("cemu_downscale"):
        setSectionConfig(
            cemuConfig, graphic_root, "DownscaleFilter", system.config["cemu_downscale"]
        )
    else:
        setSectionConfig(cemuConfig, graphic_root, "DownscaleFilter", "0")  # Bilinear
    # Aspect Ratio
    if system.isOptSet("cemu_aspect"):
        setSectionConfig(
            cemuConfig, graphic_root, "FullscreenScaling", system.config["cemu_aspect"]
        )
    else:
        setSectionConfig(cemuConfig, graphic_root, "FullscreenScaling", "0")  # Bilinear

    # [GRAPHICS OVERLAYS] - Currently disbaled! Causes crash
    # Performance - alternative to MongHud
    setSectionConfig(cemuConfig, graphic_root, "Overlay", "")
    overlay_root = getRoot(cemuConfig, "Overlay")
    # Display FPS / CPU / GPU / RAM
    if system.isOptSet("cemu_overlay") and system.config["cemu_overlay"] == "True":
        setSectionConfig(cemuConfig, overlay_root, "Position", "3")
        setSectionConfig(cemuConfig, overlay_root, "TextColor", "4294967295")
        setSectionConfig(cemuConfig, overlay_root, "TextScale", "100")
        setSectionConfig(cemuConfig, overlay_root, "FPS", "true")
        setSectionConfig(cemuConfig, overlay_root, "DrawCalls", "true")
        setSectionConfig(cemuConfig, overlay_root, "CPUUsage", "true")
        setSectionConfig(cemuConfig, overlay_root, "CPUPerCoreUsage", "true")
        setSectionConfig(cemuConfig, overlay_root, "RAMUsage", "true")
        setSectionConfig(cemuConfig, overlay_root, "VRAMUsage", "true")
    else:
        setSectionConfig(cemuConfig, overlay_root, "Position", "3")
        setSectionConfig(cemuConfig, overlay_root, "TextColor", "4294967295")
        setSectionConfig(cemuConfig, overlay_root, "TextScale", "100")
        setSectionConfig(cemuConfig, overlay_root, "FPS", "false")
        setSectionConfig(cemuConfig, overlay_root, "DrawCalls", "false")
        setSectionConfig(cemuConfig, overlay_root, "CPUUsage", "false")
        setSectionConfig(cemuConfig, overlay_root, "CPUPerCoreUsage", "false")
        setSectionConfig(cemuConfig, overlay_root, "RAMUsage", "false")
        setSectionConfig(cemuConfig, overlay_root, "VRAMUsage", "false")
    # Notifications
    setSectionConfig(cemuConfig, graphic_root, "Notification", "")
    notification_root = getRoot(cemuConfig, "Notification")
    if (
        system.isOptSet("cemu_notifications")
        and system.config["cemu_notifications"] == "True"
    ):
        setSectionConfig(cemuConfig, notification_root, "Position", "1")
        setSectionConfig(cemuConfig, notification_root, "TextColor", "4294967295")
        setSectionConfig(cemuConfig, notification_root, "TextScale", "100")
        setSectionConfig(cemuConfig, notification_root, "ControllerProfiles", "true")
        setSectionConfig(cemuConfig, notification_root, "ControllerBattery", "true")
        setSectionConfig(cemuConfig, notification_root, "ShaderCompiling", "true")
        setSectionConfig(cemuConfig, notification_root, "FriendService", "true")
    else:
        setSectionConfig(cemuConfig, notification_root, "Position", "1")
        setSectionConfig(cemuConfig, notification_root, "TextColor", "4294967295")
        setSectionConfig(cemuConfig, notification_root, "TextScale", "100")
        setSectionConfig(cemuConfig, notification_root, "ControllerProfiles", "false")
        setSectionConfig(cemuConfig, notification_root, "ControllerBattery", "false")
        setSectionConfig(cemuConfig, notification_root, "ShaderCompiling", "false")
        setSectionConfig(cemuConfig, notification_root, "FriendService", "false")

    # [AUDIO]
    setSectionConfig(cemuConfig, xml_root, "Audio", "")
    audio_root = getRoot(cemuConfig, "Audio")
    # Use cubeb (curently the only option for linux)
    setSectionConfig(cemuConfig, audio_root, "api", "3")
    # Turn audio ONLY on TV
    if system.isOptSet("cemu_audio_channels"):
        setSectionConfig(
            cemuConfig, audio_root, "TVChannels", system.config["cemu_audio_channels"]
        )
    else:
        setSectionConfig(cemuConfig, audio_root, "TVChannels", "1")  # Stereo
    # Set volume to the max
    setSectionConfig(cemuConfig, audio_root, "TVVolume", "100")
    # Set the audio device - we choose the 1st device as this is more likely the answer
    # pactl list sinks-raw | sed -e s+"^sink=[0-9]* name=\([^ ]*\) .*"+"\1"+ | sed 1q | tr -d '\n'
    proc = run(["/usr/bin/cemu/get-audio-device"], stdout=PIPE)
    cemuAudioDevice = proc.stdout.decode("utf-8")
    eslog.debug(f"*** audio device = {cemuAudioDevice} ***")
    if system.isOptSet("cemu_audio_config") and system.getOptBoolean(
        "cemu_audio_config"
    ):
        setSectionConfig(cemuConfig, audio_root, "TVDevice", cemuAudioDevice)
    elif system.isOptSet("cemu_audio_config") and not system.getOptBoolean(
        "cemu_audio_config"
    ):
        # don't change the config setting
        eslog.debug("*** use config audio device ***")
    else:
        setSectionConfig(cemuConfig, audio_root, "TVDevice", cemuAudioDevice)


# Show mouse for touchscreen actions
def getMouseMode(config: Any, rom: str) -> bool:
    return "cemu_touchpad" in config and config["cemu_touchpad"] == "1"


def getRoot(config: Any, name: str):
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section


def setSectionConfig(config: Any, xml_section: Any, name: str, value: str) -> None:
    xml_elt = xml_section.getElementsByTagName(name)
    if len(xml_elt) == 0:
        xml_elt = config.createElement(name)
        xml_section.appendChild(xml_elt)
    else:
        xml_elt = xml_elt[0]

    if xml_elt.hasChildNodes():
        xml_elt.firstChild.data = value
    else:
        xml_elt.appendChild(config.createTextNode(value))


# Language setting
def getLangFromEnvironment():
    if "LANG" in environ:
        return environ["LANG"][:5]
    return "en_US"


def getCemuLang(lang: str) -> int:
    availableLanguages = {
        "ja_JP": 0,
        "en_US": 1,
        "fr_FR": 2,
        "de_DE": 3,
        "it_IT": 4,
        "es_ES": 5,
        "zh_CN": 6,
        "ko_KR": 7,
        "nl_NL": 8,
        "pt_PT": 9,
        "ru_RU": 10,
        "zh_TW": 11,
    }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
