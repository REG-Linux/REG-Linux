"""
Consolidated Bezel Configuration Writer - Combines common functionality from different emulator managers.
"""

from typing import Dict, Optional, Tuple, Any
from pathlib import Path
from configgen.bezel.bezel_base import BezelUtils, eslog
from configgen.systemFiles import OVERLAY_CONFIG_FILE
from json import load
from os import path, makedirs, remove, listdir, unlink, symlink


def writeBezelConfig(
    generator,
    bezel,
    shaderBezel,
    retroarchConfig,
    rom,
    gameResolution,
    system,
    guns_borders_size,
):
    """Writes the bezel configuration to the emulator-specific config file."""
    # Common logic for bezel configuration across different emulators
    # disable the overlay
    # if all steps are successfully completed, enable them
    retroarchConfig["input_overlay_hide_in_menu"] = "false"
    overlay_cfg_file = OVERLAY_CONFIG_FILE

    # bezels are disabled
    # default values in case something goes wrong
    retroarchConfig["input_overlay_enable"] = "false"
    retroarchConfig["video_message_pos_x"] = 0.05
    retroarchConfig["video_message_pos_y"] = 0.05

    # special text...
    if bezel == "none" or bezel == "":
        bezel = None

    eslog.debug("libretro bezel: {}".format(bezel))

    # create a fake bezel if guns need borders
    if bezel is None and guns_borders_size is not None:
        eslog.debug("guns need border")
        gunBezelFile = "/tmp/bezel_gun_black.png"
        gunBezelInfoFile = "/tmp/bezel_gun_black.info"

        w = gameResolution["width"]
        h = gameResolution["height"]
        h5 = BezelUtils.guns_border_size(w, h)

        # could be better to calculate ratio when RA is forced to 4/3...
        ratio = generator.getInGameRatio(system.config, gameResolution, rom)
        top = h5
        left = h5
        bottom = h5
        right = h5
        if ratio == 4 / 3:
            left = (w - (h - 2 * h5) * 4 / 3) // 2
            right = left

        with open(gunBezelInfoFile, "w") as fd:
            fd.write(
                "{"
                + f' "width":{w}, "height":{h}, "top":{top}, "left":{left}, "bottom":{bottom}, "right":{right}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000'
                + "}"
            )
        BezelUtils.create_transparent_bezel(
            gunBezelFile, gameResolution["width"], gameResolution["height"]
        )
        # if the game needs a specific bezel, to draw border, consider it as a game-specific bezel, like for thebezelproject to avoid caches
        bz_infos = {
            "png": gunBezelFile,
            "info": gunBezelInfoFile,
            "layout": None,
            "mamezip": None,
            "specific_to_game": True,
        }
    else:
        if bezel is None:
            return
        # Determine emulator-specific bezelinfos lookup
        emulator_name = "unknown"
        if generator:
            cls = getattr(generator, "__class__", None)
            if cls:
                emulator_name = getattr(cls, "__name__", "unknown")
        if "libretro" in emulator_name.lower():
            bz_infos = BezelUtils.get_bezel_infos(rom, bezel, system.name, "libretro")
        else:
            bz_infos = BezelUtils.get_bezel_infos(rom, bezel, system.name, "mame")
        if bz_infos is None:
            return

    overlay_info_file = bz_infos["info"]
    overlay_png_file = bz_infos["png"]
    bezel_game = bz_infos["specific_to_game"]

    # only the png file is mandatory
    if path.exists(overlay_info_file):
        try:
            with open(overlay_info_file) as f:
                infos = load(f)
        except:
            infos = {}
    else:
        infos = {}

    # if image is not in correct size, find the correct size
    bezelNeedAdaptation = False

    if (
        "width" not in infos
        or "height" not in infos
        or "top" not in infos
        or "left" not in infos
        or "bottom" not in infos
        or "right" not in infos
        or shaderBezel
    ):
        viewPortUsed = False
    else:
        viewPortUsed = True

    gameRatio = float(gameResolution["width"]) / float(gameResolution["height"])

    if viewPortUsed:
        if (
            gameResolution["width"] != infos["width"]
            or gameResolution["height"] != infos["height"]
        ):
            if (
                gameResolution["width"] == 1080 and gameResolution["height"] == 1920
            ):  # rotated screen (RP5)
                bezelNeedAdaptation = False
            elif (
                gameResolution["width"] == 720 and gameResolution["height"] == 1280
            ):  # rotated screen (WIN600)
                bezelNeedAdaptation = False
            else:
                if (
                    gameRatio < 1.6 and guns_borders_size is None
                ):  # let's use bezels only for aspect ratios 16:10, 5:3, 16:9 and greater; don't skip if gun borders are needed
                    return
                else:
                    bezelNeedAdaptation = True
        # Ensure 720x1280 resolution uses 4:3 aspect ratio to prevent bezel misalignment
        if gameResolution["width"] == 720 and gameResolution["height"] == 1280:
            retroarchConfig["aspect_ratio_index"] = RATIO_INDEXES.index("4/3")  # Force 4:3 aspect ratio for 720x1280 resolution
        else:
            retroarchConfig["aspect_ratio_index"] = str(
                RATIO_INDEXES.index("custom")
            )  # overridden from the beginning of this file
            if is_ratio_defined("ratio", system.config):
                if system.config["ratio"] in RATIO_INDEXES:
                    retroarchConfig["aspect_ratio_index"] = RATIO_INDEXES.index(
                        system.config["ratio"]
                    )
                    retroarchConfig["video_aspect_ratio_auto"] = "false"

    else:
        # when there's no information about width and height in .info, assume TV is HD 16/9 and information is provided by the core
        if (
            gameRatio < 1.6 and guns_borders_size is None
        ):  # let's use bezels only for aspect ratios 16:10, 5:3, 16:9 and greater; don't skip if gun borders are needed
            return
        else:
            # No info about bezel, let's get width and height from the bezel image and apply
            # the usual 16:9 bezel ratios 1920x1080 (example: theBezelProject)
            try:
                infos["width"], infos["height"] = BezelUtils.fast_image_size(
                    overlay_png_file
                )
                infos["top"] = int(infos["height"] * 2 / 1080)
                infos["left"] = int(
                    infos["width"] * 241 / 1920
                )  # 241 = (1920 - (1920 / (4:3))) / 2 + 1 pixel = where viewport begins
                infos["bottom"] = int(infos["height"] * 2 / 1080)
                infos["right"] = int(infos["width"] * 241 / 1920)
                bezelNeedAdaptation = True
            except:
                pass  # well, no reason will be applied.
        if (
            gameResolution["width"] == infos["width"]
            and gameResolution["height"] == infos["height"]
        ):
            bezelNeedAdaptation = False
        if not shaderBezel:
            # Ensure 720x1280 resolution uses 4:3 aspect ratio to prevent bezel misalignment
            if gameResolution["width"] == 720 and gameResolution["height"] == 1280:
                retroarchConfig["aspect_ratio_index"] = RATIO_INDEXES.index("4/3")  # Force 4:3 aspect ratio for 720x1280 resolution
            else:
                retroarchConfig["aspect_ratio_index"] = str(RATIO_INDEXES.index("custom"))
                if (
                    is_ratio_defined("ratio", system.config)
                    and system.config["ratio"] in RATIO_INDEXES
                ):
                    retroarchConfig["aspect_ratio_index"] = RATIO_INDEXES.index(
                        system.config["ratio"]
                    )
                    retroarchConfig["video_aspect_ratio_auto"] = "false"

    if not shaderBezel:
        retroarchConfig["input_overlay_enable"] = "true"
    retroarchConfig["input_overlay_scale"] = "1.0"
    retroarchConfig["input_overlay"] = overlay_cfg_file
    retroarchConfig["input_overlay_hide_in_menu"] = "true"

    if "opacity" not in infos:
        infos["opacity"] = 1.0
    if "messagex" not in infos:
        infos["messagex"] = 0.0
    if "messagey" not in infos:
        infos["messagey"] = 0.0

    retroarchConfig["input_overlay_opacity"] = infos["opacity"]
    if retroarchConfig["aspect_ratio_index"] == str(RATIO_INDEXES.index("custom")):
        retroarchConfig["video_viewport_bias_x"] = "0.000000"
        retroarchConfig["video_viewport_bias_y"] = "0.000000"

    # stretch option
    if (
        system.isOptSet("bezel_stretch")
        and system.getOptBoolean("bezel_stretch") == True
    ):
        bezel_stretch = True
    else:
        bezel_stretch = False

    tattoo_output_png = "/tmp/bezel_tattooed.png"
    if bezelNeedAdaptation:
        wratio = gameResolution["width"] / float(infos["width"])
        hratio = gameResolution["height"] / float(infos["height"])

        # Stretch also handles cropping the bezel and adapting the viewport, if ratio is < 16:9
        if (
            gameResolution["width"] < infos["width"]
            or gameResolution["height"] < infos["height"]
        ):
            eslog.debug("Screen resolution smaller than bezel: forcing stretch")
            bezel_stretch = True
        if bezel_game is True:
            output_png_file = "/tmp/bezel_per_game.png"
            create_new_bezel_file = True
        else:
            # The logic for system bezel caching is no longer always true now that we have tattoos
            output_png_file = (
                "/tmp/"
                + path.splitext(path.basename(overlay_png_file))[0]
                + "_adapted.png"
            )
            if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
                create_new_bezel_file = True
            else:
                if (not path.exists(tattoo_output_png)) and path.exists(
                    output_png_file
                ):
                    create_new_bezel_file = False
                    eslog.debug(f"Using cached bezel file {output_png_file}")
                else:
                    try:
                        remove(tattoo_output_png)
                    except:
                        pass
                    create_new_bezel_file = True
            if create_new_bezel_file:
                fadapted = [
                    "/tmp/" + f for f in listdir("/tmp/") if (f[-12:] == "_adapted.png")
                ]
                fadapted.sort(key=lambda x: path.getmtime(x))
                # Keep only the last 10 generated bezels to save space in tmpfs /tmp
                if len(fadapted) >= 10:
                    for _ in range(10):
                        fadapted.pop()
                    eslog.debug(f"Removing unused bezel file: {fadapted}")
                    for fr in fadapted:
                        try:
                            remove(fr)
                        except:
                            pass

        if bezel_stretch:
            borderx = 0
            viewportRatio = float(infos["width"]) / float(infos["height"])
            if viewportRatio - gameRatio > 0.01:
                new_x = int(infos["width"] * gameRatio / viewportRatio)
                delta = int(infos["width"] - new_x)
                borderx = delta // 2
            eslog.debug(f"Bezel_stretch: need to cut off {borderx} pixels")
            retroarchConfig["custom_viewport_x"] = (
                infos["left"] - borderx / 2
            ) * wratio
            retroarchConfig["custom_viewport_y"] = infos["top"] * hratio
            retroarchConfig["custom_viewport_width"] = (
                infos["width"] - infos["left"] - infos["right"] + borderx
            ) * wratio
            retroarchConfig["custom_viewport_height"] = (
                infos["height"] - infos["top"] - infos["bottom"]
            ) * hratio
            retroarchConfig["video_message_pos_x"] = infos["messagex"] * wratio
            retroarchConfig["video_message_pos_y"] = infos["messagey"] * hratio
        else:
            xoffset = gameResolution["width"] - infos["width"]
            yoffset = gameResolution["height"] - infos["height"]
            retroarchConfig["custom_viewport_x"] = infos["left"] + xoffset / 2
            retroarchConfig["custom_viewport_y"] = infos["top"] + yoffset / 2
            retroarchConfig["custom_viewport_width"] = (
                infos["width"] - infos["left"] - infos["right"]
            )
            retroarchConfig["custom_viewport_height"] = (
                infos["height"] - infos["top"] - infos["bottom"]
            )
            retroarchConfig["video_message_pos_x"] = infos["messagex"] + xoffset / 2
            retroarchConfig["video_message_pos_y"] = infos["messagey"] + yoffset / 2

        if create_new_bezel_file is True:
            # Padding left and right borders for ultrawide screens (larger than 16:9 aspect ratio)
            # or up/down for 4K
            eslog.debug(f"Generating a new adapted bezel file {output_png_file}")
            try:
                BezelUtils.pad_image(
                    overlay_png_file,
                    output_png_file,
                    gameResolution["width"],
                    gameResolution["height"],
                    infos["width"],
                    infos["height"],
                    bezel_stretch,
                )
            except Exception as e:
                eslog.debug(f"Failed to create the adapated image: {e}")
                return
        overlay_png_file = (
            output_png_file  # substitute with new file (recreated or cached in /tmp)
        )
        if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
            BezelUtils.tattoo_image(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png
    else:
        if viewPortUsed:
            retroarchConfig["custom_viewport_x"] = infos["left"]
            retroarchConfig["custom_viewport_y"] = infos["top"]
            retroarchConfig["custom_viewport_width"] = (
                infos["width"] - infos["left"] - infos["right"]
            )
            retroarchConfig["custom_viewport_height"] = (
                infos["height"] - infos["top"] - infos["bottom"]
            )
        retroarchConfig["video_message_pos_x"] = infos["messagex"]
        retroarchConfig["video_message_pos_y"] = infos["messagey"]
        if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
            BezelUtils.tattoo_image(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png

    if guns_borders_size is not None:
        eslog.debug("Draw gun borders")
        output_png_file = "/tmp/bezel_gunborders.png"
        inner_size, outer_size = BezelUtils.gun_borders_size(guns_borders_size)
        BezelUtils.gun_border_image(
            overlay_png_file,
            output_png_file,
            inner_size,
            outer_size,
            BezelUtils.guns_borders_color_from_config(system.config),
        )
        overlay_png_file = output_png_file

    eslog.debug(f"Bezel file set to {overlay_png_file}")
    writeBezelCfgConfig(overlay_cfg_file, overlay_png_file)

    # For shaders that will want to use the Batocera decoration as part of the shader instead of an overlay
    if shaderBezel:
        # Create path if needed, clean old bezels
        shaderBezelPath = "/var/run/shader_bezels"
        shaderBezelFile = shaderBezelPath + "/bezel.png"
        if not path.exists(shaderBezelPath):
            makedirs(shaderBezelPath)
            eslog.debug("Creating shader bezel path {}".format(overlay_png_file))
        if path.exists(shaderBezelFile):
            eslog.debug("Removing old shader bezel {}".format(shaderBezelFile))
            if path.islink(shaderBezelFile):
                unlink(shaderBezelFile)
            else:
                remove(shaderBezelFile)

        # Link bezel png file to the fixed path.
        # Shaders should use this path to find the art.
        symlink(overlay_png_file, shaderBezelFile)
        eslog.debug(
            "Symlinked bezel file {} to {} for selected shader".format(
                overlay_png_file, shaderBezelFile
            )
        )


def writeBezelCfgConfig(cfgFile, overlay_png_file):
    """Writes the bezel configuration file."""
    fd = open(cfgFile, "w")
    fd.write("overlays = 1\n")
    fd.write('overlay0_overlay = "' + overlay_png_file + '"\n')
    fd.write("overlay0_full_screen = true\n")
    fd.write("overlay0_descs = 0\n")
    fd.close()


def is_ratio_defined(key: str, config_dict: Dict[str, Any]) -> bool:
    """Checks if a key is defined in the dictionary."""
    return (
        key in config_dict
        and isinstance(config_dict[key], str)
        and len(config_dict[key]) > 0
    )


# Define constant for ratio indices shared between emulators
# Warning: the values in the array must be exactly at the same index as
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L188
RATIO_INDEXES = [
    "4/3",
    "16/9",
    "16/10",
    "16/15",
    "21/9",
    "1/1",
    "2/1",
    "3/2",
    "3/4",
    "4/1",
    "9/16",
    "5/4",
    "6/5",
    "7/9",
    "8/3",
    "8/7",
    "19/12",
    "19/14",
    "30/17",
    "32/9",
    "config",
    "squarepixel",
    "core",
    "custom",
    "full",
]
