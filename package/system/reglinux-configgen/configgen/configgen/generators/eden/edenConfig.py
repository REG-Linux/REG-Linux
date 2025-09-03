from systemFiles import CONF
from os import environ
from subprocess import check_output, CalledProcessError
from utils.logger import get_logger

eslog = get_logger(__name__)

EDEN_CONFIG_DIR = CONF + "/eden"
EDEN_CONFIG_PATH = EDEN_CONFIG_DIR + "/qt-config.ini"
EDEN_BIN_PATH = "/usr/bin/eden-cli"


def setEdenConfig(edenConfig, system):
    # UI section
    edenConfig.ensure_section("UI")
    edenConfig.set("UI", "fullscreen", "true")
    edenConfig.set("UI", "fullscreen\\default", "true")
    edenConfig.set("UI", "confirmClose", "false")
    edenConfig.set("UI", "confirmClose\\default", "false")
    edenConfig.set("UI", "firstStart", "false")
    edenConfig.set("UI", "firstStart\\default", "false")
    edenConfig.set("UI", "displayTitleBars", "false")
    edenConfig.set("UI", "displayTitleBars\\default", "false")
    edenConfig.set("UI", "enable_discord_presence", "false")
    edenConfig.set("UI", "enable_discord_presence\\default", "false")
    edenConfig.set("UI", "calloutFlags", "1")
    edenConfig.set("UI", "calloutFlags\\default", "false")
    edenConfig.set("UI", "confirmStop", "2")
    edenConfig.set("UI", "confirmStop\\default", "false")

    # Single Window Mode
    if system.isOptSet("eden_single_window"):
        edenConfig.set("UI", "singleWindowMode", system.config["eden_single_window"])
    else:
        edenConfig.set("UI", "singleWindowMode", "true")
    edenConfig.set("UI", "singleWindowMode\\default", "false")

    edenConfig.set("UI", "hideInactiveMouse", "true")
    edenConfig.set("UI", "hideInactiveMouse\\default", "false")

    # Roms path (need for load update/dlc)
    edenConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan", "true")
    edenConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan\\default", "false")
    edenConfig.set("UI", "Paths\\gamedirs\\1\\expanded", "true")
    edenConfig.set("UI", "Paths\\gamedirs\\1\\expanded\\default", "false")
    edenConfig.set("UI", "Paths\\gamedirs\\1\\path", "/userdata/roms/switch")
    edenConfig.set("UI", "Paths\\gamedirs\\size", "1")

    edenConfig.set("UI", "Screenshots\\enable_screenshot_save_as", "true")
    edenConfig.set("UI", "Screenshots\\enable_screenshot_save_as\\default", "false")
    edenConfig.set("UI", "Screenshots\\screenshot_path", "/userdata/screenshots")
    edenConfig.set("UI", "Screenshots\\screenshot_path\\default", "false")

    # Change controller exit
    edenConfig.set(
        "UI",
        "Shortcuts\\Main%20Window\\Continue\\Pause%20Emulation\\Controller_KeySeq",
        "Home+Minus",
    )
    edenConfig.set(
        "UI",
        "Shortcuts\\Main%20Window\\Exit%20eden\\Controller_KeySeq",
        "Home+Plus",
    )

    # Data Storage section
    edenConfig.ensure_section("Data%20Storage")
    edenConfig.set(
        "Data%20Storage", "dump_directory", "/userdata/system/configs/eden/dump"
    )
    edenConfig.set("Data%20Storage", "dump_directory\\default", "false")

    edenConfig.set(
        "Data%20Storage", "load_directory", "/userdata/system/configs/eden/load"
    )
    edenConfig.set("Data%20Storage", "load_directory\\default", "false")

    edenConfig.set(
        "Data%20Storage", "nand_directory", "/userdata/system/configs/eden/nand"
    )
    edenConfig.set("Data%20Storage", "nand_directory\\default", "false")

    edenConfig.set(
        "Data%20Storage", "sdmc_directory", "/userdata/system/configs/eden/sdmc"
    )
    edenConfig.set("Data%20Storage", "sdmc_directory\\default", "false")

    edenConfig.set(
        "Data%20Storage", "tas_directory", "/userdata/system/configs/eden/tas"
    )
    edenConfig.set("Data%20Storage", "tas_directory\\default", "false")

    edenConfig.set("Data%20Storage", "use_virtual_sd", "true")
    edenConfig.set("Data%20Storage", "use_virtual_sd\\default", "false")

    # Core section
    edenConfig.ensure_section("Core")

    # Multicore
    edenConfig.set("Core", "use_multi_core", "true")
    edenConfig.set("Core", "use_multi_core\\default", "false")

    # Renderer section
    edenConfig.ensure_section("Renderer")

    # Aspect ratio
    if system.isOptSet("eden_ratio"):
        edenConfig.set("Renderer", "aspect_ratio", system.config["eden_ratio"])
    else:
        edenConfig.set("Renderer", "aspect_ratio", "0")
    edenConfig.set("Renderer", "aspect_ratio\\default", "false")

    # Graphical backend
    if system.isOptSet("eden_backend"):
        edenConfig.set("Renderer", "backend", system.config["eden_backend"])
        # Add vulkan logic
        if system.config["eden_backend"] == "1":
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
                                discrete_index = check_output(
                                    ["/usr/bin/system-vulkan", "discreteIndex"],
                                    text=True,
                                ).strip()
                                if discrete_index != "":
                                    eslog.debug(
                                        "Using Discrete GPU Index: {} for eden".format(
                                            discrete_index
                                        )
                                    )
                                    edenConfig.set(
                                        "Renderer", "vulkan_device", discrete_index
                                    )
                                    edenConfig.set(
                                        "Renderer", "vulkan_device\\default", "true"
                                    )
                                else:
                                    eslog.debug(
                                        "Couldn't get discrete GPU index, using default"
                                    )
                                    edenConfig.set("Renderer", "vulkan_device", "0")
                                    edenConfig.set(
                                        "Renderer", "vulkan_device\\default", "true"
                                    )
                            except CalledProcessError:
                                eslog.debug("Error getting discrete GPU index")
                        else:
                            eslog.debug(
                                "Discrete GPU is not available on the system. Using default."
                            )
                            edenConfig.set("Renderer", "vulkan_device", "0")
                            edenConfig.set("Renderer", "vulkan_device\\default", "true")
                    except CalledProcessError:
                        eslog.debug("Error checking for discrete GPU.")
            except CalledProcessError:
                eslog.debug("Error executing system-vulkan script.")
    else:
        edenConfig.set("Renderer", "backend", "0")
    edenConfig.set("Renderer", "backend\\default", "false")

    # Async Shader compilation
    if system.isOptSet("eden_async_shaders"):
        edenConfig.set(
            "Renderer",
            "use_asynchronous_shaders",
            system.config["eden_async_shaders"],
        )
    else:
        edenConfig.set("Renderer", "use_asynchronous_shaders", "true")
    edenConfig.set("Renderer", "use_asynchronous_shaders\\default", "false")

    # Assembly shaders
    if system.isOptSet("eden_shaderbackend"):
        edenConfig.set(
            "Renderer", "shader_backend", system.config["eden_shaderbackend"]
        )
    else:
        edenConfig.set("Renderer", "shader_backend", "0")
    edenConfig.set("Renderer", "shader_backend\\default", "false")

    # Async Gpu Emulation
    if system.isOptSet("eden_async_gpu"):
        edenConfig.set(
            "Renderer",
            "use_asynchronous_gpu_emulation",
            system.config["eden_async_gpu"],
        )
    else:
        edenConfig.set("Renderer", "use_asynchronous_gpu_emulation", "true")
    edenConfig.set("Renderer", "use_asynchronous_gpu_emulation\\default", "false")

    # NVDEC Emulation
    if system.isOptSet("eden_nvdec_emu"):
        edenConfig.set("Renderer", "nvdec_emulation", system.config["eden_nvdec_emu"])
    else:
        edenConfig.set("Renderer", "nvdec_emulation", "2")
    edenConfig.set("Renderer", "nvdec_emulation\\default", "false")

    # GPU Accuracy
    if system.isOptSet("eden_accuracy"):
        edenConfig.set("Renderer", "gpu_accuracy", system.config["eden_accuracy"])
    else:
        edenConfig.set("Renderer", "gpu_accuracy", "0")
    edenConfig.set("Renderer", "gpu_accuracy\\default", "true")

    # Vsync
    if system.isOptSet("eden_vsync"):
        edenConfig.set("Renderer", "use_vsync", system.config["eden_vsync"])
    else:
        edenConfig.set("Renderer", "use_vsync", "1")
    edenConfig.set("Renderer", "use_vsync\\default", "false")

    # Max anisotropy
    if system.isOptSet("eden_anisotropy"):
        edenConfig.set("Renderer", "max_anisotropy", system.config["eden_anisotropy"])
    else:
        edenConfig.set("Renderer", "max_anisotropy", "0")
    edenConfig.set("Renderer", "max_anisotropy\\default", "false")

    # Resolution scaler
    if system.isOptSet("eden_scale"):
        edenConfig.set("Renderer", "resolution_setup", system.config["eden_scale"])
    else:
        edenConfig.set("Renderer", "resolution_setup", "2")
    edenConfig.set("Renderer", "resolution_setup\\default", "false")

    # Scaling filter
    if system.isOptSet("eden_scale_filter"):
        edenConfig.set("Renderer", "scaling_filter", system.config["eden_scale_filter"])
    else:
        edenConfig.set("Renderer", "scaling_filter", "1")
    edenConfig.set("Renderer", "scaling_filter\\default", "false")

    # Anti aliasing method
    if system.isOptSet("eden_aliasing_method"):
        edenConfig.set(
            "Renderer", "anti_aliasing", system.config["eden_aliasing_method"]
        )
    else:
        edenConfig.set("Renderer", "anti_aliasing", "0")
    edenConfig.set("Renderer", "anti_aliasing\\default", "false")

    # CPU Section
    edenConfig.ensure_section("Cpu")

    # CPU Accuracy
    if system.isOptSet("eden_cpuaccuracy"):
        edenConfig.set("Cpu", "cpu_accuracy", system.config["eden_cpuaccuracy"])
    else:
        edenConfig.set("Cpu", "cpu_accuracy", "0")
    edenConfig.set("Cpu", "cpu_accuracy\\default", "false")

    # System section
    edenConfig.ensure_section("System")

    # Language
    if system.isOptSet("eden_language"):
        edenConfig.set("System", "language_index", system.config["eden_language"])
    else:
        edenConfig.set("System", "language_index", getLangFromEnvironment())
    edenConfig.set("System", "language_index\\default", "false")

    # Region
    if system.isOptSet("eden_region"):
        edenConfig.set("System", "region_index", system.config["eden_region"])
    else:
        edenConfig.set("System", "region_index", getRegionFromEnvironment())
    edenConfig.set("System", "region_index\\default", "false")

    # controls section
    edenConfig.ensure_section("Controls")

    # Dock Mode
    if system.isOptSet("eden_dock_mode"):
        edenConfig.set("Controls", "use_docked_mode", system.config["eden_dock_mode"])
    else:
        edenConfig.set("Controls", "use_docked_mode", "true")
    edenConfig.set("Controls", "use_docked_mode\\default", "false")

    # Sound Mode
    if system.isOptSet("eden_sound_mode"):
        edenConfig.set("Controls", "sound_index", system.config["eden_sound_mode"])
    else:
        edenConfig.set("Controls", "sound_index", "1")
    edenConfig.set("Controls", "sound_index\\default", "false")

    # Timezone
    if system.isOptSet("eden_timezone"):
        edenConfig.set("Controls", "time_zone_index", system.config["eden_timezone"])
    else:
        edenConfig.set("Controls", "time_zone_index", "0")
    edenConfig.set("Controls", "time_zone_index\\default", "false")

    # telemetry section
    edenConfig.ensure_section("WebService")
    edenConfig.set("WebService", "enable_telemetry", "false")
    edenConfig.set("WebService", "enable_telemetry\\default", "false")

    # Services section
    edenConfig.ensure_section("Services")
    edenConfig.set("Services", "bcat_backend", "none")
    edenConfig.set("Services", "bcat_backend\\default", "none")


@staticmethod
def getLangFromEnvironment():
    lang = environ["LANG"][:5]
    availableLanguages = {
        "en_US": 1,
        "fr_FR": 2,
        "de_DE": 3,
        "it_IT": 4,
        "es_ES": 5,
        "nl_NL": 8,
        "pt_PT": 9,
    }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]


@staticmethod
def getRegionFromEnvironment():
    lang = environ["LANG"][:5]
    availableRegions = {"en_US": 1, "ja_JP": 0}
    if lang in availableRegions:
        return availableRegions[lang]
    else:
        return 2  # europe
