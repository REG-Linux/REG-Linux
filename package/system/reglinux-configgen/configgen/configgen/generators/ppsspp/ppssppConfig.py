from pathlib import Path
from subprocess import CalledProcessError, check_output
from typing import Any

from configgen.settings import UnixSettings
from configgen.systemFiles import CONF, HOME_INIT
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

PPSSPP_CONFIG_DIR = str(CONF / "ppsspp" / "PSP" / "SYSTEM")
PPSSPP_CONFIG_PATH = str(CONF / "ppsspp" / "PSP" / "SYSTEM" / "ppsspp.ini")
PPSSPP_CONTROLS_PATH = str(CONF / "ppsspp" / "PSP" / "SYSTEM" / "controls.ini")
PPSSPP_CONTROLS_SOURCE_PATH = str(
    HOME_INIT / "configs" / "ppsspp" / "PSP" / "SYSTEM" / "controls.ini"
)
PPSSPP_BIN_PATH = Path("/usr/bin/PPSSPP")


def setPPSSPPConfig(system: Any) -> None:
    ppssppConfig = UnixSettings(PPSSPP_CONFIG_PATH)

    ## [GRAPHICS]
    ppssppConfig.ensure_section("Graphics")

    # Graphics Backend
    if system.isOptSet("gfxbackend"):
        ppssppConfig.set("Graphics", "GraphicsBackend", system.config["gfxbackend"])
    else:
        ppssppConfig.set("Graphics", "GraphicsBackend", "0 (OPENGL)")
    # If Vulkan
    if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == "3 (VULKAN)":
        # Check if we have a discrete GPU & if so, set the Name
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
                            discrete_name = check_output(
                                ["/usr/bin/system-vulkan", "discreteName"], text=True
                            ).strip()
                            if discrete_name != "":
                                eslog.debug(
                                    f"Using Discrete GPU Name: {discrete_name} for PPSSPP"
                                )
                                ppssppConfig.set(
                                    "Graphics", "VulkanDevice", discrete_name
                                )
                            else:
                                eslog.debug("Couldn't get discrete GPU Name")
                        except CalledProcessError:
                            eslog.debug("Error getting discrete GPU Name")
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
                ppssppConfig.set("Graphics", "GraphicsBackend", "0 (OPENGL)")
        except CalledProcessError:
            eslog.debug("Error executing system-vulkan script.")

    # Display FPS
    if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
        ppssppConfig.set(
            "Graphics", "ShowFPSCounter", "3"
        )  # 1 for Speed%, 2 for FPS, 3 for both
    else:
        ppssppConfig.set("Graphics", "ShowFPSCounter", "0")

    # Frameskip
    ppssppConfig.set("Graphics", "FrameSkipType", "0")  # Use number and not percent
    if system.isOptSet("frameskip") and system.config["frameskip"] != "automatic":
        ppssppConfig.set("Graphics", "FrameSkip", str(system.config["frameskip"]))
    elif system.isOptSet("rendering_mode") and not system.getOptBoolean(
        "rendering_mode"
    ):
        ppssppConfig.set("Graphics", "FrameSkip", "0")
    else:
        ppssppConfig.set("Graphics", "FrameSkip", "2")

    # Buffered rendering
    if system.isOptSet("rendering_mode") and not system.getOptBoolean("rendering_mode"):
        ppssppConfig.set("Graphics", "RenderingMode", "0")
        # Have to force autoframeskip off here otherwise PPSSPP sets rendering mode back to 1.
        ppssppConfig.set("Graphics", "AutoFrameSkip", "False")
    else:
        ppssppConfig.set("Graphics", "RenderingMode", "1")
        # Both internal resolution and auto frameskip are dependent on buffered rendering being on, only check these if the user is actually using buffered rendering.
        # Internal Resolution
        if system.isOptSet("internal_resolution"):
            ppssppConfig.set(
                "Graphics",
                "InternalResolution",
                str(system.config["internal_resolution"]),
            )
        else:
            ppssppConfig.set("Graphics", "InternalResolution", "1")
        # Auto frameskip
        if system.isOptSet("autoframeskip") and not system.getOptBoolean(
            "autoframeskip"
        ):
            ppssppConfig.set("Graphics", "AutoFrameSkip", "False")
        else:
            ppssppConfig.set("Graphics", "AutoFrameSkip", "True")

    # VSync Interval
    if system.isOptSet("vsyncinterval") and not system.getOptBoolean("vsyncinterval"):
        ppssppConfig.set("Graphics", "VSyncInterval", "False")
    else:
        ppssppConfig.set("Graphics", "VSyncInterval", "True")

    # Texture Scaling Level
    if system.isOptSet("texture_scaling_level"):
        ppssppConfig.set(
            "Graphics", "TexScalingLevel", system.config["texture_scaling_level"]
        )
    else:
        ppssppConfig.set("Graphics", "TexScalingLevel", "1")
    # Texture Scaling Type
    if system.isOptSet("texture_scaling_type"):
        ppssppConfig.set(
            "Graphics", "TexScalingType", system.config["texture_scaling_type"]
        )
    else:
        ppssppConfig.set("Graphics", "TexScalingType", "0")
    # Texture Deposterize
    if system.isOptSet("texture_deposterize"):
        ppssppConfig.set(
            "Graphics", "TexDeposterize", system.config["texture_deposterize"]
        )
    else:
        ppssppConfig.set("Graphics", "TexDeposterize", "True")

    # Anisotropic Filtering
    if system.isOptSet("anisotropic_filtering"):
        ppssppConfig.set(
            "Graphics", "AnisotropyLevel", system.config["anisotropic_filtering"]
        )
    else:
        ppssppConfig.set("Graphics", "AnisotropyLevel", "3")
    # Texture Filtering
    if system.isOptSet("texture_filtering"):
        ppssppConfig.set(
            "Graphics", "TextureFiltering", system.config["texture_filtering"]
        )
    else:
        ppssppConfig.set("Graphics", "TextureFiltering", "1")

    ## [SYSTEM PARAM]
    ppssppConfig.ensure_section("SystemParam")

    # Forcing Nickname to Anonymous or User name
    if (
        system.isOptSet("retroachievements")
        and system.getOptBoolean("retroachievements")
        and system.isOptSet("retroachievements.username")
        and system.config.get("retroachievements.username", "") != ""
    ):
        ppssppConfig.set(
            "SystemParam",
            "NickName",
            system.config.get("retroachievements.username", ""),
        )
    else:
        ppssppConfig.set("SystemParam", "NickName", "Anonymous")
    # Disable Encrypt Save (permit to exchange save with different machines)
    ppssppConfig.set("SystemParam", "EncryptSave", "False")

    ## [GENERAL]
    ppssppConfig.ensure_section("General")

    # Rewinding
    if system.isOptSet("rewind") and system.getOptBoolean("rewind"):
        ppssppConfig.set(
            "General", "RewindFlipFrequency", "300"
        )  # 300 = every 5 seconds
    else:
        ppssppConfig.set("General", "RewindFlipFrequency", "0")
    # Cheats
    if system.isOptSet("enable_cheats"):
        ppssppConfig.set("General", "EnableCheats", system.config["enable_cheats"])
    else:
        ppssppConfig.set("General", "EnableCheats", "False")
    # Don't check for a new version
    ppssppConfig.set("General", "CheckForNewVersion", "False")

    ## [UPGRADE] - don't upgrade
    ppssppConfig.ensure_section("Upgrade")
    ppssppConfig.set("Upgrade", "UpgradeMessage", "")
    ppssppConfig.set("Upgrade", "UpgradeVersion", "")
    ppssppConfig.set("Upgrade", "DismissedVersion", "")

    # Custom : allow the user to configure directly PPSSPP via system.conf via lines like : ppsspp.section.option=value
    for user_config in system.config:
        if user_config[:7] == "ppsspp.":
            section_option = user_config[7:]
            section_option_splitter = section_option.find(".")
            custom_section = section_option[:section_option_splitter]
            custom_option = section_option[section_option_splitter + 1 :]
            ppssppConfig.ensure_section(custom_section)
            ppssppConfig.set(
                custom_section, custom_option, str(system.config[user_config])
            )

    ppssppConfig.write()
