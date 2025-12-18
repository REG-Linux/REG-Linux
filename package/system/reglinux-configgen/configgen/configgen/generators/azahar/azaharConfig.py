from os import environ
from subprocess import check_output, CalledProcessError
from configgen.systemFiles import CONF
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


AZAHAR_CONFIG_PATH = CONF + "/azahar-emu/qt-config.ini"
AZAHAR_BIN_PATH = "/usr/bin/azahar"


# Language auto setting
def getAzaharLangFromEnvironment():
    region = {
        "AUTO": -1,
        "JPN": 0,
        "USA": 1,
        "EUR": 2,
        "AUS": 3,
        "CHN": 4,
        "KOR": 5,
        "TWN": 6,
    }
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
        "zh_TW": "TWN",
    }
    lang = environ["LANG"][:5]
    return region.get(availableLanguages.get(lang, "AUTO"), -1)


def setAzaharConfig(azaharConfig, system):
    # [LAYOUT]
    if "Layout" not in azaharConfig:
        azaharConfig["Layout"] = {}
    azaharConfig.set("Layout", "custom_layout", "false")
    azaharConfig.set("Layout", "custom_layout\\default", "true")

    if system.isOptSet("azahar_screen_layout"):
        tab = system.config["azahar_screen_layout"].split("-")
        azaharConfig.set("Layout", "swap_screen", tab[1])
        azaharConfig.set("Layout", "layout_option", tab[0])
    else:
        azaharConfig.set("Layout", "swap_screen", "false")
        azaharConfig.set("Layout", "layout_option", "0")

    azaharConfig.set("Layout", "swap_screen\\default", "false")
    azaharConfig.set("Layout", "layout_option\\default", "false")

    ## [SYSTEM]if "Layout" not in azaharConfig:
    if "System" not in azaharConfig:
        azaharConfig["System"] = {}
    if (
        system.isOptSet("azahar_is_new_3ds")
        and system.config["azahar_is_new_3ds"] == "1"
    ):
        azaharConfig.set("System", "is_new_3ds", "true")
    else:
        azaharConfig.set("System", "is_new_3ds", "false")
    azaharConfig.set("System", "is_new_3ds\\default", "false")
    azaharConfig.set("System", "region_value", str(getAzaharLangFromEnvironment()))
    azaharConfig.set("System", "region_value\\default", "false")

    ## [UI]
    if "UI" not in azaharConfig:
        azaharConfig["UI"] = {}
    azaharConfig.set("UI", "fullscreen", "true")
    azaharConfig.set("UI", "fullscreen\\default", "false")
    azaharConfig.set("UI", "displayTitleBars", "false")
    azaharConfig.set("UI", "displaytitlebars", "false")
    azaharConfig.set("UI", "displayTitleBars\\default", "false")
    azaharConfig.set("UI", "firstStart", "false")
    azaharConfig.set("UI", "firstStart\\default", "false")
    azaharConfig.set("UI", "hideInactiveMouse", "true")
    azaharConfig.set("UI", "hideInactiveMouse\\default", "false")
    azaharConfig.set("UI", "enable_discord_presence", "false")
    azaharConfig.set("UI", "enable_discord_presence\\default", "false")
    azaharConfig.set("UI", "calloutFlags", "1")
    azaharConfig.set("UI", "calloutFlags\\default", "false")
    azaharConfig.set("UI", "confirmClose", "false")
    azaharConfig.set("UI", "confirmclose", "false")
    azaharConfig.set("UI", "confirmClose\\default", "false")
    azaharConfig.set("UI", "Paths\\screenshotPath", "/userdata/screenshots")
    azaharConfig.set("UI", "Paths\\screenshotPath\\default", "false")
    azaharConfig.set("UI", "Updater\\check_for_update_on_start", "false")
    azaharConfig.set("UI", "Updater\\check_for_update_on_start\\default", "false")

    ## [RENDERER]
    if "Renderer" not in azaharConfig:
        azaharConfig["Renderer"] = {}
    azaharConfig.set("Renderer", "use_hw_renderer", "true")
    azaharConfig.set("Renderer", "use_hw_shader", "true")
    azaharConfig.set("Renderer", "use_shader_jit", "true")

    if system.isOptSet("azahar_graphics_api"):
        azaharConfig.set(
            "Renderer", "graphics_api", system.config["azahar_graphics_api"]
        )
    else:
        azaharConfig.set("Renderer", "graphics_api", "1")

    if (
        system.isOptSet("azahar_graphics_api")
        and system.config["azahar_graphics_api"] == "2"
    ):
        try:
            have_vulkan = check_output(
                ["/usr/bin/system-vulkan", "hasVulkan"], text=True
            ).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available.")
                try:
                    have_discrete = check_output(
                        ["/usr/bin/system-vulkan", "hasDiscrete"], text=True
                    ).strip()
                    if have_discrete == "true":
                        discrete_index = check_output(
                            ["/usr/bin/system-vulkan", "discreteIndex"], text=True
                        ).strip()
                        if discrete_index:
                            azaharConfig.set(
                                "Renderer", "physical_device", discrete_index
                            )
                except CalledProcessError:
                    eslog.debug("Error checking for discrete GPU.")
        except CalledProcessError:
            eslog.debug("Error executing system-vulkan script.")

    if (
        system.isOptSet("azahar_use_vsync_new")
        and system.config["azahar_use_vsync_new"] == "0"
    ):
        azaharConfig.set("Renderer", "use_vsync_new", "false")
    else:
        azaharConfig.set("Renderer", "use_vsync_new", "true")
    azaharConfig.set("Renderer", "use_vsync_new\\default", "true")

    if system.isOptSet("azahar_resolution_factor"):
        azaharConfig.set(
            "Renderer", "resolution_factor", system.config["azahar_resolution_factor"]
        )
    else:
        azaharConfig.set("Renderer", "resolution_factor", "1")
    azaharConfig.set("Renderer", "resolution_factor\\default", "false")

    if (
        system.isOptSet("azahar_async_shader_compilation")
        and system.config["azahar_async_shader_compilation"] == "1"
    ):
        azaharConfig.set("Renderer", "async_shader_compilation", "true")
    else:
        azaharConfig.set("Renderer", "async_shader_compilation", "false")
    azaharConfig.set("Renderer", "async_shader_compilation\\default", "false")

    if (
        system.isOptSet("azahar_use_frame_limit")
        and system.config["azahar_use_frame_limit"] == "0"
    ):
        azaharConfig.set("Renderer", "use_frame_limit", "false")
    else:
        azaharConfig.set("Renderer", "use_frame_limit", "true")

    ## [WEB SERVICE]
    if "WebService" not in azaharConfig:
        azaharConfig["WebService"] = {}
    azaharConfig.set("WebService", "enable_telemetry", "false")

    ## [UTILITY]
    if "Utility" not in azaharConfig:
        azaharConfig["Utility"] = {}
    if (
        system.isOptSet("azahar_use_disk_shader_cache")
        and system.config["azahar_use_disk_shader_cache"] == "1"
    ):
        azaharConfig.set("Utility", "use_disk_shader_cache", "true")
    else:
        azaharConfig.set("Utility", "use_disk_shader_cache", "false")
    azaharConfig.set("Utility", "use_disk_shader_cache\\default", "false")

    if (
        system.isOptSet("azahar_custom_textures")
        and system.config["azahar_custom_textures"] != "0"
    ):
        tab = system.config["azahar_custom_textures"].split("-")
        azaharConfig.set("Utility", "custom_textures", "true")
        if tab[1] == "normal":
            azaharConfig.set("Utility", "async_custom_loading", "true")
            azaharConfig.set("Utility", "preload_textures", "false")
        else:
            azaharConfig.set("Utility", "async_custom_loading", "false")
            azaharConfig.set("Utility", "preload_textures", "true")
    else:
        azaharConfig.set("Utility", "custom_textures", "false")
        azaharConfig.set("Utility", "preload_textures", "false")

    azaharConfig.set("Utility", "async_custom_loading\\default", "true")
    azaharConfig.set("Utility", "custom_textures\\default", "false")
    azaharConfig.set("Utility", "preload_textures\\default", "false")

    return azaharConfig
