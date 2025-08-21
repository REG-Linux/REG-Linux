from systemFiles import CONF
from os import environ
from subprocess import check_output, CalledProcessError

from utils.logger import get_logger
eslog = get_logger(__name__)

AZAHAR_CONFIG_PATH = CONF + '/azahar-emu/qt-config.ini'
AZAHAR_BIN_PATH = '/usr/bin/azahar'

# Language auto setting
def getAzaharLangFromEnvironment():
    region = { "AUTO": -1, "JPN": 0, "USA": 1, "EUR": 2, "AUS": 3, "CHN": 4, "KOR": 5, "TWN": 6 }
    availableLanguages = {
        "ja_JP": "JPN",
        "en_US": "USA",
        "de_DE": "EUR",
        "es_ES": "EUR",
        "fr_FR": "EUR",
        "it_IT": "EUR",
        "hu_HU": "EUR",
        "pt_PT": "EUR",
        "ru_RU": "EUR",
        "en_AU": "AUS",
        "zh_CN": "CHN",
        "ko_KR": "KOR",
        "zh_TW": "TWN"
    }
    lang = environ['LANG'][:5]
    if lang in availableLanguages:
        return region[availableLanguages[lang]]
    else:
        return region["AUTO"]

@staticmethod
def setAzaharConfig(azaharConfig, system):
    ## [LAYOUT]
    if not azaharConfig.has_section("Layout"):
        azaharConfig.add_section("Layout")

    # Screen Layout
    azaharConfig.set("Layout", "custom_layout", "false")
    azaharConfig.set("Layout", "custom_layout\\default", "true")
    if system.isOptSet('azahar_screen_layout'):
        tab = system.config["azahar_screen_layout"].split('-')
        azaharConfig.set("Layout", "swap_screen",   tab[1])
        azaharConfig.set("Layout", "layout_option", tab[0])
    else:
        azaharConfig.set("Layout", "swap_screen", "false")
        azaharConfig.set("Layout", "layout_option", "0")
    azaharConfig.set("Layout", "swap_screen\\default", "false")
    azaharConfig.set("Layout", "layout_option\\default", "false")

    ## [SYSTEM]
    if not azaharConfig.has_section("System"):
        azaharConfig.add_section("System")
    # New 3DS Version
    if system.isOptSet('azahar_is_new_3ds') and system.config["azahar_is_new_3ds"] == '1':
        azaharConfig.set("System", "is_new_3ds", "true")
    else:
        azaharConfig.set("System", "is_new_3ds", "false")
    azaharConfig.set("System", "is_new_3ds\\default", "false")
    # Language
    azaharConfig.set("System", "region_value", str(getAzaharLangFromEnvironment()))
    azaharConfig.set("System", "region_value\\default", "false")

    ## [UI]
    if not azaharConfig.has_section("UI"):
        azaharConfig.add_section("UI")
    # Start Fullscreen
    azaharConfig.set("UI", "fullscreen", "true")
    azaharConfig.set("UI", "fullscreen\\default", "false")

    # Defaults
    azaharConfig.set("UI", "displayTitleBars", "false")
    azaharConfig.set("UI", "displaytitlebars", "false") # Emulator Bug
    azaharConfig.set("UI", "displayTitleBars\\default", "false")
    azaharConfig.set("UI", "firstStart", "false")
    azaharConfig.set("UI", "firstStart\\default", "false")
    azaharConfig.set("UI", "hideInactiveMouse", "true")
    azaharConfig.set("UI", "hideInactiveMouse\\default", "false")
    azaharConfig.set("UI", "enable_discord_presence", "false")
    azaharConfig.set("UI", "enable_discord_presence\\default", "false")

    # Remove pop-up prompt on start
    azaharConfig.set("UI", "calloutFlags", "1")
    azaharConfig.set("UI", "calloutFlags\\default", "false")
    # Close without confirmation
    azaharConfig.set("UI", "confirmClose", "false")
    azaharConfig.set("UI", "confirmclose", "false") # Emulator Bug
    azaharConfig.set("UI", "confirmClose\\default", "false")

    # screenshots
    azaharConfig.set("UI", "Paths\\screenshotPath", "/userdata/screenshots")
    azaharConfig.set("UI", "Paths\\screenshotPath\\default", "false")

    # don't check updates
    azaharConfig.set("UI", "Updater\\check_for_update_on_start", "false")
    azaharConfig.set("UI", "Updater\\check_for_update_on_start\\default", "false")

    ## [RENDERER]
    if not azaharConfig.has_section("Renderer"):
        azaharConfig.add_section("Renderer")
    # Force Hardware Rrendering / Shader or nothing works fine
    azaharConfig.set("Renderer", "use_hw_renderer", "true")
    azaharConfig.set("Renderer", "use_hw_shader",   "true")
    azaharConfig.set("Renderer", "use_shader_jit",  "true")
    # Software, OpenGL (default) or Vulkan
    if system.isOptSet('azahar_graphics_api'):
        azaharConfig.set("Renderer", "graphics_api", system.config["azahar_graphics_api"])
    else:
        azaharConfig.set("Renderer", "graphics_api", "1")
    # Set Vulkan as necessary
    if system.isOptSet("azahar_graphics_api") and system.config["azahar_graphics_api"] == "2":
        try:
            have_vulkan = check_output(["/usr/bin/system-vulkan", "hasVulkan"], text=True).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    have_discrete = check_output(["/usr/bin/system-vulkan", "hasDiscrete"], text=True).strip()
                    if have_discrete == "true":
                        eslog.debug("A discrete GPU is available on the system. We will use that for performance")
                        try:
                            discrete_index = check_output(["/usr/bin/system-vulkan", "discreteIndex"], text=True).strip()
                            if discrete_index != "":
                                eslog.debug("Using Discrete GPU Index: {} for Citra".format(discrete_index))
                                azaharConfig.set("Renderer", "physical_device", discrete_index)
                            else:
                                eslog.debug("Couldn't get discrete GPU index")
                        except CalledProcessError:
                            eslog.debug("Error getting discrete GPU index")
                    else:
                        eslog.debug("Discrete GPU is not available on the system. Trying integrated.")
                        have_integrated = check_output(["/usr/bin/system-vulkan", "hasIntegrated"], text=True).strip()
                        if have_integrated == "true":
                            eslog.debug("Using integrated GPU to provide Vulkan. Beware of performance")
                            try:
                                integrated_index = check_output(["/usr/bin/system-vulkan", "integratedIndex"], text=True).strip()
                                if integrated_index != "":
                                    eslog.debug("Using Integrated GPU Index: {} for Citra".format(integrated_index))
                                    azaharConfig.set("Renderer", "physical_device", integrated_index)
                                else:
                                    eslog.debug("Couldn't get integrated GPU index")
                            except CalledProcessError:
                                eslog.debug("Error getting integrated GPU index")
                        else:
                            eslog.debug("Integrated GPU is not available on the system. Cannot enable Vulkan.")
                except CalledProcessError:
                    eslog.debug("Error checking for discrete GPU.")
        except CalledProcessError:
            eslog.debug("Error executing system-vulkan script.")
    # Use VSYNC
    if system.isOptSet('azahar_use_vsync_new') and system.config["azahar_use_vsync_new"] == '0':
        azaharConfig.set("Renderer", "use_vsync_new", "false")
    else:
        azaharConfig.set("Renderer", "use_vsync_new", "true")
    azaharConfig.set("Renderer", "use_vsync_new\\default", "true")
    # Resolution Factor
    if system.isOptSet('azahar_resolution_factor'):
        azaharConfig.set("Renderer", "resolution_factor", system.config["azahar_resolution_factor"])
    else:
        azaharConfig.set("Renderer", "resolution_factor", "1")
    azaharConfig.set("Renderer", "resolution_factor\\default", "false")
    # Async Shader Compilation
    if system.isOptSet('azahar_async_shader_compilation') and system.config["azahar_async_shader_compilation"] == '1':
        azaharConfig.set("Renderer", "async_shader_compilation", "true")
    else:
        azaharConfig.set("Renderer", "async_shader_compilation", "false")
    azaharConfig.set("Renderer", "async_shader_compilation\\default", "false")
    # Use Frame Limit
    if system.isOptSet('azahar_use_frame_limit') and system.config["azahar_use_frame_limit"] == '0':
        azaharConfig.set("Renderer", "use_frame_limit", "false")
    else:
        azaharConfig.set("Renderer", "use_frame_limit", "true")

    ## [WEB SERVICE]
    if not azaharConfig.has_section("WebService"):
        azaharConfig.add_section("WebService")
    azaharConfig.set("WebService", "enable_telemetry",  "false")

    ## [UTILITY]
    if not azaharConfig.has_section("Utility"):
        azaharConfig.add_section("Utility")
    # Disk Shader Cache
    if system.isOptSet('azahar_use_disk_shader_cache') and system.config["azahar_use_disk_shader_cache"] == '1':
        azaharConfig.set("Utility", "use_disk_shader_cache", "true")
    else:
        azaharConfig.set("Utility", "use_disk_shader_cache", "false")
    azaharConfig.set("Utility", "use_disk_shader_cache\\default", "false")
    # Custom Textures
    if system.isOptSet('azahar_custom_textures') and system.config["azahar_custom_textures"] != '0':
        tab = system.config["azahar_custom_textures"].split('-')
        azaharConfig.set("Utility", "custom_textures",  "true")
        if tab[1] == 'normal':
            azaharConfig.set("Utility", "async_custom_loading", "true")
            azaharConfig.set("Utility", "preload_textures", "false")
        else:
            azaharConfig.set("Utility", "async_custom_loading", "false")
            azaharConfig.set("Utility", "preload_textures", "true")
    else:
        azaharConfig.set("Utility", "custom_textures",  "false")
        azaharConfig.set("Utility", "preload_textures", "false")
    azaharConfig.set("Utility", "async_custom_loading\\default", "true")
    azaharConfig.set("Utility", "custom_textures\\default", "false")
    azaharConfig.set("Utility", "preload_textures\\default", "false")
