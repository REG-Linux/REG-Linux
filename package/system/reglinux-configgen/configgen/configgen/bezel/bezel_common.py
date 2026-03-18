"""Consolidated Bezel Configuration Writer - Combines common functionality from different emulator managers."""

from contextlib import suppress
from json import load
from os import listdir
from pathlib import Path
from typing import Any

from configgen.bezel.bezel_base import BezelUtils, eslog
from configgen.config.paths import OVERLAY_CONFIG_FILE

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


def _is_ratio_defined(key: str, config_dict: dict[str, Any]) -> bool:
    """Check if a key is defined in the dictionary."""
    return (
        key in config_dict
        and isinstance(config_dict[key], str)
        and len(config_dict[key]) > 0
    )


def _create_gun_borders_bezel(
    game_resolution: dict[str, int],
    generator: Any,
    system: Any,
    rom: str,
) -> dict[str, Any]:
    """Create a fake bezel for gun borders."""
    gun_bezel_file = "/tmp/bezel_gun_black.png"
    gun_bezel_info_file = "/tmp/bezel_gun_black.info"

    width = game_resolution["width"]
    height = game_resolution["height"]
    border_size = BezelUtils.guns_border_size(width, height)

    ratio = generator.getInGameRatio(system.config, game_resolution, rom)
    top = border_size
    left = border_size
    bottom = border_size
    right = border_size

    if ratio == 4 / 3:
        left = (width - (height - 2 * border_size) * 4 / 3) // 2
        right = left

    Path(gun_bezel_info_file).write_text(
        "{"
        f'"width":{width}, "height":{height}, "top":{top}, "left":{left}, '
        f'"bottom":{bottom}, "right":{right}, "opacity":1.0000000, '
        f'"messagex":0.220000, "messagey":0.120000'
        "}",
    )
    BezelUtils.create_transparent_bezel(gun_bezel_file, width, height)

    return {
        "png": gun_bezel_file,
        "info": gun_bezel_info_file,
        "layout": None,
        "mamezip": None,
        "specific_to_game": True,
    }


def _get_bezel_infos(
    bezel: str,
    rom: str,
    system_name: str,
    generator: Any,
) -> dict[str, Any] | None:
    """Get bezel information based on emulator type."""
    emulator_name = "unknown"
    if generator:
        cls = getattr(generator, "__class__", None)
        if cls:
            emulator_name = getattr(cls, "__name__", "unknown")

    if "libretro" in emulator_name.lower():
        return BezelUtils.get_bezel_infos(rom, bezel, system_name, "libretro")
    return BezelUtils.get_bezel_infos(rom, bezel, system_name, "mame")


def _load_bezel_info(overlay_info_file: str) -> dict[str, Any]:
    """Load bezel info from file."""
    if not Path(overlay_info_file).exists():
        return {}

    try:
        with Path(overlay_info_file).open() as f:
            return load(f)
    except Exception:
        return {}


def _check_bezel_needs_adaptation(
    infos: dict[str, Any],
    game_resolution: dict[str, int],
    game_ratio: float,
    guns_borders_size: str | None,
    shader_bezel: bool,
) -> tuple[bool | None, bool]:
    """Check if bezel needs adaptation and if viewport is used.

    Returns:
        tuple: (needs_adaptation, view_port_used)
               needs_adaptation can be None to signal skip

    """
    if shader_bezel or any(
        key not in infos
        for key in ["width", "height", "top", "left", "bottom", "right"]
    ):
        return False, False

    view_port_used = True

    if (
        game_resolution["width"] != infos["width"]
        or game_resolution["height"] != infos["height"]
    ):
        # Rotated screens
        if (game_resolution["width"] == 1080 and game_resolution["height"] == 1920) or (
            game_resolution["width"] == 720 and game_resolution["height"] == 1280
        ):
            return False, view_port_used

        if game_ratio < 1.6 and guns_borders_size is None:
            return None, False  # Signal to skip

        return True, view_port_used

    return False, view_port_used


def _extract_bezel_dimensions_from_image(
    overlay_png_file: str,
    game_resolution: dict[str, int],
    game_ratio: float,
    guns_borders_size: str | None,
) -> dict[str, Any] | None:
    """Extract bezel dimensions from image when no info file is available."""
    if game_ratio < 1.6 and guns_borders_size is None:
        return None

    try:
        width, height = BezelUtils.fast_image_size(overlay_png_file)
        return {
            "width": width,
            "height": height,
            "top": int(height * 2 / 1080),
            "left": int(width * 241 / 1920),
            "bottom": int(height * 2 / 1080),
            "right": int(width * 241 / 1920),
        }
    except Exception:
        return None


def _set_aspect_ratio_config(
    retroarch_config: dict[str, Any],
    game_resolution: dict[str, int],
    system_config: dict[str, Any],
) -> None:
    """Configure aspect ratio settings."""
    if game_resolution["width"] == 720 and game_resolution["height"] == 1280:
        retroarch_config["aspect_ratio_index"] = RATIO_INDEXES.index("4/3")
    else:
        retroarch_config["aspect_ratio_index"] = str(RATIO_INDEXES.index("custom"))
        if (
            _is_ratio_defined("ratio", system_config)
            and system_config["ratio"] in RATIO_INDEXES
        ):
            retroarch_config["aspect_ratio_index"] = RATIO_INDEXES.index(
                system_config["ratio"],
            )
    retroarch_config["video_aspect_ratio_auto"] = "false"


def _calculate_viewport_stretch(
    infos: dict[str, Any],
    game_resolution: dict[str, int],
    game_ratio: float,
) -> tuple[float, float, int]:
    """Calculate viewport dimensions for stretch mode."""
    width_ratio = game_resolution["width"] / float(infos["width"])
    height_ratio = game_resolution["height"] / float(infos["height"])

    viewport_ratio = float(infos["width"]) / float(infos["height"])
    border_x = 0

    if viewport_ratio - game_ratio > 0.01:
        new_x = int(infos["width"] * game_ratio / viewport_ratio)
        delta = int(infos["width"] - new_x)
        border_x = delta // 2

    return width_ratio, height_ratio, border_x


def _set_stretch_viewport(
    retroarch_config: dict[str, Any],
    infos: dict[str, Any],
    width_ratio: float,
    height_ratio: float,
    border_x: int,
) -> None:
    """Set viewport configuration for stretch mode."""
    retroarch_config["custom_viewport_x"] = (infos["left"] - border_x / 2) * width_ratio
    retroarch_config["custom_viewport_y"] = infos["top"] * height_ratio
    retroarch_config["custom_viewport_width"] = (
        infos["width"] - infos["left"] - infos["right"] + border_x
    ) * width_ratio
    retroarch_config["custom_viewport_height"] = (
        infos["height"] - infos["top"] - infos["bottom"]
    ) * height_ratio
    retroarch_config["video_message_pos_x"] = infos["messagex"] * width_ratio
    retroarch_config["video_message_pos_y"] = infos["messagey"] * height_ratio


def _set_normal_viewport(
    retroarch_config: dict[str, Any],
    infos: dict[str, Any],
    game_resolution: dict[str, int],
) -> None:
    """Set viewport configuration for normal (non-stretch) mode."""
    x_offset = float(game_resolution["width"] - infos["width"])
    y_offset = float(game_resolution["height"] - infos["height"])

    retroarch_config["custom_viewport_x"] = infos["left"] + x_offset / 2
    retroarch_config["custom_viewport_y"] = infos["top"] + y_offset / 2
    retroarch_config["custom_viewport_width"] = (
        infos["width"] - infos["left"] - infos["right"]
    )
    retroarch_config["custom_viewport_height"] = (
        infos["height"] - infos["top"] - infos["bottom"]
    )
    retroarch_config["video_message_pos_x"] = infos["messagex"] + x_offset / 2
    retroarch_config["video_message_pos_y"] = infos["messagey"] + y_offset / 2


def _cleanup_old_adapted_bezels() -> None:
    """Clean up old adapted bezel files to save space."""
    adapted_files = [
        "/tmp/" + f for f in listdir("/tmp/") if f.endswith("_adapted.png")
    ]
    adapted_files.sort(key=lambda x: Path(x).stat().st_mtime)

    if len(adapted_files) >= 10:
        for file_to_remove in adapted_files[: len(adapted_files) - 10]:
            eslog.debug(f"Removing unused bezel file: {file_to_remove}")
            with suppress(Exception):
                Path(file_to_remove).unlink()


def _should_create_new_bezel_file(
    output_png_file: str,
    tattoo_output_png: str,
    system: Any,
) -> bool:
    """Determine if a new bezel file should be created or if cached can be used."""
    if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
        return True

    tattoo_path = Path(tattoo_output_png)
    output_path = Path(output_png_file)

    if not tattoo_path.exists() and output_path.exists():
        eslog.debug(f"Using cached bezel file {output_png_file}")
        return False

    with suppress(Exception):
        Path(tattoo_output_png).unlink()
    return True


def _adapt_bezel_image(
    overlay_png_file: str,
    output_png_file: str,
    game_resolution: dict[str, int],
    infos: dict[str, Any],
    bezel_stretch: bool,
) -> bool:
    """Adapt bezel image to game resolution."""
    eslog.debug(f"Generating a new adapted bezel file {output_png_file}")
    try:
        BezelUtils.pad_image(
            overlay_png_file,
            output_png_file,
            game_resolution["width"],
            game_resolution["height"],
            infos["width"],
            infos["height"],
            bezel_stretch,
        )
        return True
    except Exception as e:
        eslog.debug(f"Failed to create the adapted image: {e}")
        return False


def _setup_shader_bezel(overlay_png_file: str) -> None:
    """Set up shader bezel symlink."""
    shader_bezel_path = Path("/var/run/shader_bezels")
    shader_bezel_file = shader_bezel_path / "bezel.png"

    if not shader_bezel_path.exists():
        shader_bezel_path.mkdir(parents=True, exist_ok=True)
        eslog.debug(f"Creating shader bezel path {overlay_png_file}")

    if shader_bezel_file.exists():
        eslog.debug(f"Removing old shader bezel {shader_bezel_file}")
        shader_bezel_file.unlink()

    Path(str(shader_bezel_file)).symlink_to(overlay_png_file)
    eslog.debug(
        f"Symlinked bezel file {overlay_png_file} to {shader_bezel_file} for selected shader",
    )


def writeBezelConfig(
    generator: Any,
    bezel: str | None,
    shader_bezel: bool,
    retroarch_config: dict[str, Any],
    rom: str,
    game_resolution: dict[str, int],
    system: Any,
    guns_borders_size: str | None,
) -> None:
    """Write the bezel configuration to the emulator-specific config file."""
    overlay_cfg_file = OVERLAY_CONFIG_FILE

    # Initialize with defaults (bezels disabled)
    retroarch_config["input_overlay_hide_in_menu"] = "false"
    retroarch_config["input_overlay_enable"] = "false"
    retroarch_config["video_message_pos_x"] = 0.05
    retroarch_config["video_message_pos_y"] = 0.05

    # Normalize bezel value
    if bezel in ("none", ""):
        bezel = None

    eslog.debug(f"libretro bezel: {bezel}")

    # Handle gun borders bezel creation
    if bezel is None and guns_borders_size is not None:
        eslog.debug("guns need border")
        bz_infos = _create_gun_borders_bezel(game_resolution, generator, system, rom)
    else:
        if bezel is None:
            return
        bz_infos = _get_bezel_infos(bezel, rom, system.name, generator)
        if bz_infos is None:
            return

    # Extract overlay file paths
    overlay_info_file = str(bz_infos.get("info", ""))
    overlay_png_file = str(bz_infos.get("png", ""))
    bezel_game = bool(bz_infos.get("specific_to_game", False))

    # Load bezel info
    infos = _load_bezel_info(overlay_info_file)

    # Calculate game ratio
    game_ratio = float(game_resolution["width"]) / float(game_resolution["height"])

    # Check if bezel needs adaptation
    bezel_needs_adaptation, view_port_used = _check_bezel_needs_adaptation(
        infos, game_resolution, game_ratio, guns_borders_size, shader_bezel
    )

    if bezel_needs_adaptation is None:
        return  # Aspect ratio not suitable for bezels

    # Handle case when no viewport info is available
    if not view_port_used:
        extracted_dims = _extract_bezel_dimensions_from_image(
            overlay_png_file, game_resolution, game_ratio, guns_borders_size
        )
        if extracted_dims is None:
            return
        infos.update(extracted_dims)
        bezel_needs_adaptation = True

        if not shader_bezel:
            _set_aspect_ratio_config(retroarch_config, game_resolution, system.config)
    else:
        # Viewport is available
        if game_resolution["width"] == 720 and game_resolution["height"] == 1280:
            retroarch_config["aspect_ratio_index"] = RATIO_INDEXES.index("4/3")
        else:
            retroarch_config["aspect_ratio_index"] = str(RATIO_INDEXES.index("custom"))
            if (
                _is_ratio_defined("ratio", system.config)
                and system.config["ratio"] in RATIO_INDEXES
            ):
                retroarch_config["aspect_ratio_index"] = RATIO_INDEXES.index(
                    system.config["ratio"],
                )
        retroarch_config["video_aspect_ratio_auto"] = "false"

    # Enable overlay
    if not shader_bezel:
        retroarch_config["input_overlay_enable"] = "true"
    retroarch_config["input_overlay_scale"] = "1.0"
    retroarch_config["input_overlay"] = overlay_cfg_file
    retroarch_config["input_overlay_hide_in_menu"] = "true"

    # Set defaults for optional info fields
    for key, default in [("opacity", 1.0), ("messagex", 0.0), ("messagey", 0.0)]:
        if key not in infos:
            infos[key] = default

    retroarch_config["input_overlay_opacity"] = infos["opacity"]

    if retroarch_config["aspect_ratio_index"] == str(RATIO_INDEXES.index("custom")):
        retroarch_config["video_viewport_bias_x"] = "0.000000"
        retroarch_config["video_viewport_bias_y"] = "0.000000"

    # Handle bezel stretch setting
    bezel_stretch = system.isOptSet("bezel_stretch") and system.getOptBoolean(
        "bezel_stretch"
    )

    tattoo_output_png = "/tmp/bezel_tattooed.png"

    if bezel_needs_adaptation:
        _process_adapted_bezel(
            overlay_png_file,
            game_resolution,
            infos,
            game_ratio,
            bezel_stretch,
            bezel_game,
            system,
            tattoo_output_png,
            retroarch_config,
        )
    else:
        _process_normal_bezel(
            infos,
            view_port_used,
            system,
            tattoo_output_png,
            overlay_png_file,
            retroarch_config,
        )

    # Apply gun borders if needed
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
    writeBezelCfgConfig(str(overlay_cfg_file), overlay_png_file)

    # Handle shader bezel
    if shader_bezel:
        _setup_shader_bezel(overlay_png_file)


def writeBezelCfgConfig(cfg_file: str, overlay_png_file: str) -> None:
    """Write the bezel configuration file."""
    with Path(cfg_file).open("w") as fd:
        fd.write("overlays = 1\n")
        fd.write('overlay0_overlay = "' + overlay_png_file + '"\n')
        fd.write("overlay0_full_screen = true\n")
        fd.write("overlay0_descs = 0\n")


def _process_adapted_bezel(
    overlay_png_file: str,
    game_resolution: dict[str, int],
    infos: dict[str, Any],
    game_ratio: float,
    bezel_stretch: bool,
    bezel_game: bool,
    system: Any,
    tattoo_output_png: str,
    retroarch_config: dict[str, Any],
) -> None:
    """Process bezel that needs adaptation to game resolution."""
    width_ratio, height_ratio, border_x = _calculate_viewport_stretch(
        infos, game_resolution, game_ratio
    )

    # Force stretch if screen is smaller than bezel
    if (
        game_resolution["width"] < infos["width"]
        or game_resolution["height"] < infos["height"]
    ):
        eslog.debug("Screen resolution smaller than bezel: forcing stretch")
        bezel_stretch = True

    # Determine output file and whether to create new
    if bezel_game:
        output_png_file = "/tmp/bezel_per_game.png"
        create_new = True
    else:
        output_png_file = "/tmp/" + Path(overlay_png_file).stem + "_adapted.png"
        create_new = _should_create_new_bezel_file(
            output_png_file, tattoo_output_png, system
        )
        if not create_new:
            _cleanup_old_adapted_bezels()

    # Set viewport based on stretch mode
    if bezel_stretch:
        _set_stretch_viewport(
            retroarch_config, infos, width_ratio, height_ratio, border_x
        )
    else:
        _set_normal_viewport(retroarch_config, infos, game_resolution)

    # Create adapted bezel if needed
    if create_new and _adapt_bezel_image(
        overlay_png_file, output_png_file, game_resolution, infos, bezel_stretch
    ):
        overlay_png_file = output_png_file

    # Apply tattoo if configured
    if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
        BezelUtils.tattoo_image(overlay_png_file, tattoo_output_png, system)
        overlay_png_file = tattoo_output_png


def _process_normal_bezel(
    infos: dict[str, Any],
    view_port_used: bool,
    system: Any,
    tattoo_output_png: str,
    overlay_png_file: str,
    retroarch_config: dict[str, Any],
) -> None:
    """Process bezel that doesn't need adaptation."""
    if view_port_used:
        retroarch_config["custom_viewport_x"] = infos["left"]
        retroarch_config["custom_viewport_y"] = infos["top"]
        retroarch_config["custom_viewport_width"] = (
            infos["width"] - infos["left"] - infos["right"]
        )
        retroarch_config["custom_viewport_height"] = (
            infos["height"] - infos["top"] - infos["bottom"]
        )

    retroarch_config["video_message_pos_x"] = infos["messagex"]
    retroarch_config["video_message_pos_y"] = infos["messagey"]

    # Apply tattoo if configured
    if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
        BezelUtils.tattoo_image(overlay_png_file, tattoo_output_png, system)
