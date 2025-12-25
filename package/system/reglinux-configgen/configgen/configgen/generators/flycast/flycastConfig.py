from typing import Any, Dict

from configgen.systemFiles import BIOS, CONF, SAVES

FLYCAST_CONFIG_DIR = CONF + "/flycast"
FLYCAST_CONFIG_PATH = FLYCAST_CONFIG_DIR + "/emu.cfg"
FLYCAST_SAVES_DIR = SAVES + "/dreamcast"
FLYCAST_BIOS_DIR = BIOS + "/dc"
FLYCAST_VMU_BLANK_PATH = (
    "/usr/share/reglinux/configgen/data/dreamcast/vmu_save_blank.bin"
)
FLYCAST_VMU_A1_PATH = FLYCAST_SAVES_DIR + "/flycast/vmu_save_A1.bin"
FLYCAST_VMU_A2_PATH = FLYCAST_SAVES_DIR + "/flycast/vmu_save_A2.bin"
FLYCAST_BIN_PATH = "/usr/bin/flycast"


def setFlycastConfig(
    flycastConfig: Any, system: Any, gameResolution: Dict[str, int]
) -> None:
    if not flycastConfig.has_section("input"):
        flycastConfig.add_section("input")

    if not flycastConfig.has_section("config"):
        flycastConfig.add_section("config")

    if not flycastConfig.has_section("window"):
        flycastConfig.add_section("window")

    # ensure we are always fullscreen
    flycastConfig.set("window", "fullscreen", "yes")

    # set video resolution
    flycastConfig.set("window", "width", str(gameResolution["width"]))
    flycastConfig.set("window", "height", str(gameResolution["height"]))

    # set render resolution - default 480 (Native)
    if system.isOptSet("flycast_render_resolution"):
        flycastConfig.set(
            "config", "rend.Resolution", str(system.config["flycast_render_resolution"])
        )
    else:
        flycastConfig.set("config", "rend.Resolution", "480")

    # wide screen mode - default off
    if system.isOptSet("flycast_ratio"):
        flycastConfig.set(
            "config", "rend.WideScreen", str(system.config["flycast_ratio"])
        )
    else:
        flycastConfig.set("config", "rend.WideScreen", "no")

    # rotate option - default off
    if system.isOptSet("flycast_rotate"):
        flycastConfig.set(
            "config", "rend.Rotate90", str(system.config["flycast_rotate"])
        )
    else:
        flycastConfig.set("config", "rend.Rotate90", "no")

    # renderer - default: OpenGL
    if system.isOptSet("flycast_renderer") and system.config["flycast_renderer"] == "0":
        if (
            system.isOptSet("flycast_sorting")
            and system.config["flycast_sorting"] == "3"
        ):
            # per pixel
            flycastConfig.set("config", "pvr.rend", "3")
        else:
            # per triangle
            flycastConfig.set("config", "pvr.rend", "0")
    elif (
        system.isOptSet("flycast_renderer") and system.config["flycast_renderer"] == "4"
    ):
        if (
            system.isOptSet("flycast_sorting")
            and system.config["flycast_sorting"] == "3"
        ):
            # per pixel
            flycastConfig.set("config", "pvr.rend", "5")
        else:
            # per triangle
            flycastConfig.set("config", "pvr.rend", "4")
    else:
        flycastConfig.set("config", "pvr.rend", "0")
        if (
            system.isOptSet("flycast_sorting")
            and system.config["flycast_sorting"] == "3"
        ):
            # per pixel
            flycastConfig.set("config", "pvr.rend", "3")
    # anisotropic filtering
    if system.isOptSet("flycast_anisotropic"):
        flycastConfig.set(
            "config",
            "rend.AnisotropicFiltering",
            str(system.config["flycast_anisotropic"]),
        )
    else:
        flycastConfig.set("config", "rend.AnisotropicFiltering", "1")

    # transparent sorting
    # per strip
    if system.isOptSet("flycast_sorting") and system.config["flycast_sorting"] == "2":
        flycastConfig.set("config", "rend.PerStripSorting", "yes")
    else:
        flycastConfig.set("config", "rend.PerStripSorting", "no")

    # [Dreamcast specifics]
    # language
    if system.isOptSet("flycast_language"):
        flycastConfig.set(
            "config", "Dreamcast.Language", str(system.config["flycast_language"])
        )
    else:
        flycastConfig.set("config", "Dreamcast.Language", "1")

    # region
    if system.isOptSet("flycast_region"):
        flycastConfig.set(
            "config", "Dreamcast.Region", str(system.config["flycast_language"])
        )
    else:
        flycastConfig.set("config", "Dreamcast.Region", "1")

    # save / load states
    if system.isOptSet("flycast_loadstate"):
        flycastConfig.set(
            "config", "Dreamcast.AutoLoadState", str(system.config["flycast_loadstate"])
        )
    else:
        flycastConfig.set("config", "Dreamcast.AutoLoadState", "no")
    if system.isOptSet("flycast_savestate"):
        flycastConfig.set(
            "config", "Dreamcast.AutoSaveState", str(system.config["flycast_savestate"])
        )
    else:
        flycastConfig.set("config", "Dreamcast.AutoSaveState", "no")

    # windows CE
    if system.isOptSet("flycast_winCE"):
        flycastConfig.set(
            "config", "Dreamcast.ForceWindowsCE", str(system.config["flycast_winCE"])
        )
    else:
        flycastConfig.set("config", "Dreamcast.ForceWindowsCE", "no")

    # DSP
    if system.isOptSet("flycast_DSP"):
        flycastConfig.set(
            "config", "aica.DSPEnabled", str(system.config["flycast_DSP"])
        )
    else:
        flycastConfig.set("config", "aica.DSPEnabled", "no")

    # Guns (WIP)
    # Guns crosshairs
    if system.isOptSet("flycast_lightgun1_crosshair"):
        flycastConfig.set(
            "config",
            "rend.CrossHairColor1",
            str(system.config["flycast_lightgun1_crosshair"]),
        )
    else:
        flycastConfig.set("config", "rend.CrossHairColor1", "0")
    if system.isOptSet("flycast_lightgun2_crosshair"):
        flycastConfig.set(
            "config",
            "rend.CrossHairColor2",
            str(system.config["flycast_lightgun2_crosshair"]),
        )
    else:
        flycastConfig.set("config", "rend.CrossHairColor2", "0")
    if system.isOptSet("flycast_lightgun3_crosshair"):
        flycastConfig.set(
            "config",
            "rend.CrossHairColor3",
            str(system.config["flycast_lightgun3_crosshair"]),
        )
    else:
        flycastConfig.set("config", "rend.CrossHairColor3", "0")
    if system.isOptSet("flycast_lightgun4_crosshair"):
        flycastConfig.set(
            "config",
            "rend.CrossHairColor4",
            str(system.config["flycast_lightgun4_crosshair"]),
        )
    else:
        flycastConfig.set("config", "rend.CrossHairColor4", "0")

    # custom: allow the user to configure directly emu.cfg via system.conf via lines like: dreamcast.flycast.section.option=value
    for user_config in system.config:
        if user_config[:8] == "flycast.":
            section_option = user_config[8:]
            section_option_splitter = section_option.find(".")
            custom_section = section_option[:section_option_splitter]
            custom_option = section_option[section_option_splitter + 1 :]
            if not flycastConfig.has_section(custom_section):
                flycastConfig.add_section(custom_section)
            flycastConfig.set(custom_section, custom_option, system.config[user_config])
