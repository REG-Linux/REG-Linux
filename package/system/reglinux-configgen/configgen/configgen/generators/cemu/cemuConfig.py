import os
import codecs
import subprocess
from systemFiles import CONF, BIOS
from os import environ
from xml.dom import minidom

from utils.logger import get_logger
eslog = get_logger(__name__)

cemuConfig  = CONF + '/cemu'
cemuConfigFile = cemuConfig + '/settings.xml'
cemuBios = BIOS + '/cemu'
cemuProfilesDir = cemuConfig + 'controllerProfiles'
cemuRomdir = '/userdata/roms/wiiu'
cemuSaves = '/userdata/saves/wiiu'
cemuBin = '/usr/bin/cemu/cemu'

def CemuConfig(configFile, system):

    # bios pack
    if not os.path.isdir(cemuBios):
        os.mkdir(cemuBios)
    if not os.path.isdir(cemuConfig):
        os.mkdir(cemuConfig)
    # graphic packs
    if not os.path.isdir(cemuSaves + "/graphicPacks"):
        os.mkdir(cemuSaves + "/graphicPacks")
    if not os.path.isdir(cemuConfig + "/controllerProfiles"):
        os.mkdir(cemuConfig + "/controllerProfiles")

    # Config file
    config = minidom.Document()
    if os.path.exists(configFile):
        try:
            config = minidom.parse(configFile)
        except:
            pass # reinit the file

    ## [ROOT]
    xml_root = getRoot(config, "content")
    # Default mlc path
    setSectionConfig(config, xml_root, "mlc_path", cemuSaves)
    # Remove auto updates
    setSectionConfig(config, xml_root, "check_update", "false")
    # Avoid the welcome window
    setSectionConfig(config, xml_root, "gp_download", "true")
    # Other options
    setSectionConfig(config, xml_root, "logflag", "0")
    setSectionConfig(config, xml_root, "advanced_ppc_logging", "false")
    setSectionConfig(config, xml_root, "use_discord_presence", "false")
    setSectionConfig(config, xml_root, "fullscreen_menubar", "false")
    setSectionConfig(config, xml_root, "vk_warning", "false")
    setSectionConfig(config, xml_root, "fullscreen", "true")
    # Language
    if not system.isOptSet("cemu_console_language") or system.config["cemu_console_language"] == "ui":
        lang = getLangFromEnvironment()
    else:
        lang = system.config["cemu_console_language"]
    setSectionConfig(config, xml_root, "console_language", str(getCemuLang(lang)))

    ## [WINDOWS]
    # Position
    setSectionConfig(config, xml_root, "window_position", "")
    window_position = getRoot(config, "window_position")
    setSectionConfig(config, window_position, "x", "0")
    setSectionConfig(config, window_position, "y", "0")
    # Size
    setSectionConfig(config, xml_root, "window_size", "")
    window_size = getRoot(config, "window_size")
    setSectionConfig(config, window_size, "x", "640")
    setSectionConfig(config, window_size, "y", "480")

    ## [GAMEPAD]
    if system.isOptSet("cemu_gamepad") and system.config["cemu_gamepad"] == "True":
        setSectionConfig(config, xml_root, "open_pad", "true")
    else:
        setSectionConfig(config, xml_root, "open_pad", "false")
    setSectionConfig(config, xml_root, "pad_position", "")
    pad_position = getRoot(config, "pad_position")
    setSectionConfig(config, pad_position, "x", "0")
    setSectionConfig(config, pad_position, "y", "0")
    # Size
    setSectionConfig(config, xml_root, "pad_size", "")
    pad_size = getRoot(config, "pad_size")
    setSectionConfig(config, pad_size, "x", "640")
    setSectionConfig(config, pad_size, "y", "480")

    ## [GAME PATH]
    setSectionConfig(config, xml_root, "GamePaths", "")
    game_root = getRoot(config, "GamePaths")
    # Default games path
    setSectionConfig(config, game_root, "Entry", cemuRomdir)

    ## [GRAPHICS]
    setSectionConfig(config, xml_root, "Graphic", "")
    graphic_root = getRoot(config, "Graphic")
    # Graphical backend
    if system.isOptSet("cemu_gfxbackend"):
        api_value = system.config["cemu_gfxbackend"]
    else:
        api_value = "1"  # Vulkan
    setSectionConfig(config, graphic_root, "api", api_value)
    # Only set the graphics `device` if Vulkan
    if api_value == "1":
        # Check if we have a discrete GPU & if so, set the UUID
        try:
            have_vulkan = subprocess.check_output(["/usr/bin/system-vulkan", "hasVulkan"], text=True).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    have_discrete = subprocess.check_output(["/usr/bin/system-vulkan", "hasDiscrete"], text=True).strip()
                    if have_discrete == "true":
                        eslog.debug("A discrete GPU is available on the system. We will use that for performance")
                        try:
                            discrete_uuid = subprocess.check_output(["/usr/bin/system-vulkan", "discreteUUID"], text=True).strip()
                            if discrete_uuid != "":
                                discrete_uuid_num = discrete_uuid.replace("-", "")
                                eslog.debug("Using Discrete GPU UUID: {} for Cemu".format(discrete_uuid_num))
                                setSectionConfig(config, graphic_root, "device", discrete_uuid_num)
                            else:
                                eslog.debug("Couldn't get discrete GPU UUID!")
                        except subprocess.CalledProcessError:
                            eslog.debug("Error getting discrete GPU UUID!")
                    else:
                        eslog.debug("Discrete GPU is not available on the system. Using default.")
                except subprocess.CalledProcessError:
                    eslog.debug("Error checking for discrete GPU.")
            else:
                eslog.debug("Vulkan driver is not available on the system. Falling back to OpenGL")
                setSectionConfig(config, graphic_root, "api", "0")
        except subprocess.CalledProcessError:
            eslog.debug("Error executing system-vulkan script.")

    # Async VULKAN Shader compilation
    if system.isOptSet("cemu_async") and system.config["cemu_async"] == "False":
        setSectionConfig(config, graphic_root, "AsyncCompile", "false")
    else:
        setSectionConfig(config, graphic_root, "AsyncCompile", "true")
    # Vsync
    if system.isOptSet("cemu_vsync"):
        setSectionConfig(config, graphic_root, "VSync", system.config["cemu_vsync"])
    else:
        setSectionConfig(config, graphic_root, "VSync", "0") # Off
    # Upscale Filter
    if system.isOptSet("cemu_upscale"):
        setSectionConfig(config, graphic_root, "UpscaleFilter", system.config["cemu_upscale"])
    else:
        setSectionConfig(config, graphic_root, "UpscaleFilter", "2") # Hermite
    # Downscale Filter
    if system.isOptSet("cemu_downscale"):
        setSectionConfig(config, graphic_root, "DownscaleFilter", system.config["cemu_downscale"])
    else:
        setSectionConfig(config, graphic_root, "DownscaleFilter", "0") # Bilinear
    # Aspect Ratio
    if system.isOptSet("cemu_aspect"):
        setSectionConfig(config, graphic_root, "FullscreenScaling", system.config["cemu_aspect"])
    else:
        setSectionConfig(config, graphic_root, "FullscreenScaling", "0") # Bilinear

    ## [GRAPHICS OVERLAYS] - Currently disbaled! Causes crash
    # Performance - alternative to MongHud
    setSectionConfig(config, graphic_root, "Overlay", "")
    overlay_root = getRoot(config, "Overlay")
    # Display FPS / CPU / GPU / RAM
    if system.isOptSet("cemu_overlay") and system.config["cemu_overlay"] == "True":
        setSectionConfig(config, overlay_root, "Position",        "3")
        setSectionConfig(config, overlay_root, "TextColor",       "4294967295")
        setSectionConfig(config, overlay_root, "TextScale",       "100")
        setSectionConfig(config, overlay_root, "FPS",             "true")
        setSectionConfig(config, overlay_root, "DrawCalls",       "true")
        setSectionConfig(config, overlay_root, "CPUUsage",        "true")
        setSectionConfig(config, overlay_root, "CPUPerCoreUsage", "true")
        setSectionConfig(config, overlay_root, "RAMUsage",        "true")
        setSectionConfig(config, overlay_root, "VRAMUsage",       "true")
    else:
        setSectionConfig(config, overlay_root, "Position",        "3")
        setSectionConfig(config, overlay_root, "TextColor",       "4294967295")
        setSectionConfig(config, overlay_root, "TextScale",       "100")
        setSectionConfig(config, overlay_root, "FPS",             "false")
        setSectionConfig(config, overlay_root, "DrawCalls",       "false")
        setSectionConfig(config, overlay_root, "CPUUsage",        "false")
        setSectionConfig(config, overlay_root, "CPUPerCoreUsage", "false")
        setSectionConfig(config, overlay_root, "RAMUsage",        "false")
        setSectionConfig(config, overlay_root, "VRAMUsage",       "false")
    # Notifications
    setSectionConfig(config, graphic_root, "Notification", "")
    notification_root = getRoot(config, "Notification")
    if system.isOptSet("cemu_notifications") and system.config["cemu_notifications"] == "True":
        setSectionConfig(config, notification_root, "Position", "1")
        setSectionConfig(config, notification_root, "TextColor", "4294967295")
        setSectionConfig(config, notification_root, "TextScale", "100")
        setSectionConfig(config, notification_root, "ControllerProfiles", "true")
        setSectionConfig(config, notification_root, "ControllerBattery",  "true")
        setSectionConfig(config, notification_root, "ShaderCompiling",    "true")
        setSectionConfig(config, notification_root, "FriendService",      "true")
    else:
        setSectionConfig(config, notification_root, "Position", "1")
        setSectionConfig(config, notification_root, "TextColor", "4294967295")
        setSectionConfig(config, notification_root, "TextScale", "100")
        setSectionConfig(config, notification_root, "ControllerProfiles", "false")
        setSectionConfig(config, notification_root, "ControllerBattery",  "false")
        setSectionConfig(config, notification_root, "ShaderCompiling",    "false")
        setSectionConfig(config, notification_root, "FriendService",      "false")

    ## [AUDIO]
    setSectionConfig(config, xml_root, "Audio", "")
    audio_root = getRoot(config, "Audio")
    # Use cubeb (curently the only option for linux)
    setSectionConfig(config, audio_root, "api", "3")
    # Turn audio ONLY on TV
    if system.isOptSet("cemu_audio_channels"):
        setSectionConfig(config, audio_root, "TVChannels", system.config["cemu_audio_channels"])
    else:
        setSectionConfig(config, audio_root, "TVChannels", "1") # Stereo
    # Set volume to the max
    setSectionConfig(config, audio_root, "TVVolume", "100")
    # Set the audio device - we choose the 1st device as this is more likely the answer
    # pactl list sinks-raw | sed -e s+"^sink=[0-9]* name=\([^ ]*\) .*"+"\1"+ | sed 1q | tr -d '\n'
    proc = subprocess.run(["/usr/bin/cemu/get-audio-device"], stdout=subprocess.PIPE)
    cemuAudioDevice = proc.stdout.decode('utf-8')
    eslog.debug("*** audio device = {} ***".format(cemuAudioDevice))
    if system.isOptSet("cemu_audio_config") and system.getOptBoolean("cemu_audio_config") == True:
        setSectionConfig(config, audio_root, "TVDevice", cemuAudioDevice)
    elif system.isOptSet("cemu_audio_config") and system.getOptBoolean("cemu_audio_config") == False:
        # don't change the config setting
        eslog.debug("*** use config audio device ***")
    else:
        setSectionConfig(config, audio_root, "TVDevice", cemuAudioDevice)

    # Save the config file
    xml = open(configFile, "w")

    # TODO: python 3 - workaround to encode files in utf-8
    xml = codecs.open(configFile, "w", "utf-8")
    dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
    xml.write(dom_string)

# Show mouse for touchscreen actions
def getMouseMode(self, config, rom):
    if "cemu_touchpad" in config and config["cemu_touchpad"] == "1":
        return True
    else:
        return False

def getRoot(config, name):
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def setSectionConfig(config, xml_section, name, value):
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
    if 'LANG' in environ:
        return environ['LANG'][:5]
    else:
        return "en_US"

def getCemuLang(lang):
    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "zh_CN": 6, "ko_KR": 7, "nl_NL": 8, "pt_PT": 9, "ru_RU": 10, "zh_TW": 11 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]
