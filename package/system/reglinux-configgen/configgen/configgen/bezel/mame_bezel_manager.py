"""
Module responsible for managing bezel configurations for the MAME emulator.
"""

import os
import shutil
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from configgen.bezel.bezel_base import BezelUtils, IBezelManager
from configgen.utils.logger import get_logger

logger = get_logger(__name__)

# Constants
MAINTAIN_ASPECT_RATIO_WIDTH_HEIGHT = 4 / 3  # Assumption for bezel aspect ratio
TATTOO_WIDTH_REFERENCE = 240  # Half the difference between 4:3 and 16:9 on 1920px
TATTOO_VERTICAL_MARGIN = 20  # Vertical margin for tattoo placement
DEFAULT_RESOLUTION = (1920, 1080)  # Fallback resolution


def getMameMachineSize(rom_base: str, tmp_zip_dir: str) -> tuple[int, int, int]:
    """
    Get machine size information for MAME ROM.

    Args:
        rom_base: Base name of the ROM file
        tmp_zip_dir: Temporary directory for artwork files

    Returns:
        Tuple of (width, height, rotation) for the MAME machine
    """
    # Placeholder implementation - in real scenario this would extract machine info from MAME
    # For now, returning default values to avoid undefined variable error
    width, height = DEFAULT_RESOLUTION
    rotation = 0  # Default to no rotation

    # In a real implementation, this function would analyze the ROM/machine to determine:
    # - Screen dimensions (width, height)
    # - Screen rotation (0, 90, 180, 270)
    # This might involve querying MAME executable or parsing ROM metadata

    return width, height, rotation


def setup_mame_bezels(
    system: Any,
    rom: str,
    messSys: str,
    game_resolution: Dict[str, int],
    guns: List[Any],
) -> None:
    """
    Set up bezels for MAME games, including handling gun borders and tattoos.

    Args:
        system: System configuration object
        rom: Path to the ROM file
        messSys: MESS system name if applicable
        game_resolution: Dictionary containing game resolution (width, height)
        guns: Guns configuration
    """
    bezel_set = _extract_bezel_set(system)

    try:
        guns_borders_size = _get_guns_borders_size(guns, system.config)

        writeBezelConfig(
            bezel_set, system, rom, messSys, game_resolution, guns_borders_size
        )
    except Exception as e:
        logger.warning(f"Error setting up MAME bezels: {e}")
        writeBezelConfig(None, system, rom, "", game_resolution, None)


def _extract_bezel_set(system: Any) -> Optional[str]:
    """
    Extract bezel set from system config.

    Args:
        system: System configuration object

    Returns:
        Bezel set name if available and not forced to be disabled, otherwise None
    """
    bezel_set = None
    if "bezel" in system.config and system.config["bezel"] != "":
        bezel_set = system.config["bezel"]
    if system.isOptSet("forceNoBezel") and system.getOptBoolean("forceNoBezel"):
        bezel_set = None
    return bezel_set


def _get_guns_borders_size(
    guns: List[Any], system_config: Dict[str, Any]
) -> Optional[str]:
    """
    Get guns borders size from config if guns are available.

    Args:
        guns: Guns configuration object
        system_config: System configuration dictionary

    Returns:
        Guns border size identifier if guns are configured, otherwise None
    """
    if guns is not None:
        from configgen.controllers import guns_borders_size_name

        return guns_borders_size_name(guns, system_config)
    return None


def writeBezelConfig(
    bezelSet: Optional[str],
    system: Any,
    rom: str,
    messSys: str,
    game_resolution: Dict[str, int],
    guns_borders_size: Optional[str],
) -> None:
    """Create MAME artwork configuration for bezels."""
    tmp_zip_dir: str | None = None  # Initialize to None
    try:
        rom_base = os.path.splitext(os.path.basename(rom))[0]
        tmp_zip_dir = _get_tmp_directory_path(rom_base, messSys)

        # Clean previous artwork directory
        if os.path.exists(tmp_zip_dir):
            shutil.rmtree(tmp_zip_dir)

        if bezelSet is None and guns_borders_size is None:
            return

        # Create artwork directory
        os.makedirs(tmp_zip_dir)

        # Get bezel information
        bz_infos = _get_bezel_info(bezelSet, system, rom)

        # Create transparent bezel if no info found and borders are needed
        if bz_infos is None:
            if guns_borders_size is not None:
                overlay_png_file = "/tmp/bezel_transmame_black.png"
                BezelUtils.create_transparent_bezel(
                    overlay_png_file,
                    game_resolution["width"],
                    game_resolution["height"],
                )
                bz_infos = {"png": overlay_png_file}
            else:
                return

        # Handle different bezel types and create layout
        result = _process_bezel_layout(bz_infos, rom_base, messSys, tmp_zip_dir)
        if result is not None:
            (
                png_file,
                img_width,
                img_height,
                _,  # bz_x is not used here
                _,  # bz_y is not used here
                _,  # bz_width is not used here
                _,  # bz_height is not used here
                _,  # bz_alpha is not used here
            ) = result
        else:
            # If result is None, it means mamezip was used and function should return early
            return

        # Apply tattoo if required
        if _should_apply_tattoo(system):
            png_file = _apply_tattoo(
                tmp_zip_dir, png_file, img_width, img_height, system
            )

        # Apply gun borders if required
        if guns_borders_size is not None:
            png_file = _apply_gun_borders(
                tmp_zip_dir, png_file, guns_borders_size, system.config
            )
    except Exception as e:
        logger.error(f"Error in writeBezelConfig: {e}")
        # Ensure the temp directory is cleaned up even if an error occurs
        try:
            if tmp_zip_dir is not None and os.path.exists(tmp_zip_dir):
                shutil.rmtree(tmp_zip_dir)
        except Exception:  # Catch any exception during cleanup
            pass  # Ignore errors during cleanup
        raise


def _get_tmp_directory_path(rom_base: str, mess_sys: str) -> str:
    """
    Get the temporary directory path for artwork files.

    Args:
        rom_base: Base name of the ROM file
        mess_sys: MESS system name if applicable

    Returns:
        Path to the temporary artwork directory
    """
    if mess_sys != "" and not mess_sys.startswith("/"):
        return f"/var/run/mame_artwork/{os.path.basename(mess_sys)}"
    else:
        return f"/var/run/mame_artwork/{rom_base}"


def _get_bezel_info(
    bezel_set: Optional[str], system: Any, rom: str
) -> Optional[Dict[str, Any]]:
    """
    Get bezel information from the bezel database.

    Args:
        bezel_set: Name of the bezel set to use
        system: System configuration object
        rom: Path to the ROM file

    Returns:
        Dictionary with bezel information if found, otherwise None
    """
    if bezel_set is not None:
        try:
            return BezelUtils.get_bezel_infos(rom, bezel_set, system.name, "mame")
        except Exception as e:
            logger.warning(f"Error getting bezel info for {rom}: {e}")
            return None
    return None


def _safe_file_operation(operation_func: Any, *args: Any, **kwargs: Any):
    """
    Safely perform a file operation and handle exceptions.

    Args:
        operation_func: Function to execute that performs the file operation
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the operation on success, None on failure
    """
    try:
        return operation_func(*args, **kwargs)
    except OSError as e:
        logger.warning(f"File operation failed: {e}")
        return None


def _create_symlink(src: str, dest: str):
    """
    Safely create a symlink, removing the destination if it exists.

    Args:
        src: Source file path
        dest: Destination symlink path
    """
    if os.path.exists(dest) or os.path.islink(dest):
        _safe_file_operation(os.remove, dest)
    _safe_file_operation(os.symlink, src, dest)


def _process_bezel_layout(
    bz_infos: Dict[str, Any], rom_base: str, mess_sys: str, tmp_zip_dir: str
) -> Optional[Tuple[str, int, int, int, int, int, int, float]]:
    """
    Process the bezel layout and return positioning information.

    Args:
        bz_infos: Dictionary containing bezel information
        rom_base: Base name of the ROM file
        mess_sys: MESS system name if applicable
        tmp_zip_dir: Temporary directory for artwork files

    Returns:
        Tuple containing (png_file, img_width, img_height, bz_x, bz_y, bz_width, bz_height, bz_alpha)
        if standard layout is processed, None if mamezip is processed (early return)
    """
    # Handle mamezip case
    if "mamezip" in bz_infos and os.path.exists(bz_infos["mamezip"]):
        _handle_mamezip_case(rom_base, mess_sys, bz_infos)
        # Return None to indicate early return
        return None

    # Handle layout case
    if "layout" in bz_infos and os.path.exists(bz_infos["layout"]):
        png_file = os.path.split(bz_infos["png"])[1]
        _create_symlink(bz_infos["layout"], tmp_zip_dir + "/default.lay")
        _create_symlink(bz_infos["png"], tmp_zip_dir + "/" + png_file)
        img_width, img_height = BezelUtils.fast_image_size(bz_infos["png"])
        # Return minimal defaults since exact positions not needed for layout
        return png_file, img_width, img_height, 0, 0, img_width, img_height, 1.0

    # Handle standard PNG + info file case
    return _create_standard_layout(bz_infos, rom_base, tmp_zip_dir)


def _handle_mamezip_case(
    rom_base: str, mess_sys: str, bz_infos: Dict[str, Any]
) -> None:
    """
    Handle the case where a mamezip file is available.

    Args:
        rom_base: Base name of the ROM file
        mess_sys: MESS system name if applicable
        bz_infos: Dictionary containing bezel information with mamezip path
    """
    if mess_sys != "" and not mess_sys.startswith("/"):
        art_file = f"/var/run/mame_artwork/{os.path.basename(mess_sys)}.zip"
    else:
        art_file = f"/var/run/mame_artwork/{rom_base}.zip"

    if os.path.exists(art_file):
        if os.path.islink(art_file):
            os.unlink(art_file)
        else:
            os.remove(art_file)
    _create_symlink(bz_infos["mamezip"], art_file)


def _parse_bezel_info_file(
    info_path: str, png_path: str
) -> tuple[int, int, int, int, int, int, float]:
    """
    Parse bezel info file and return position and size values.

    Args:
        info_path: Path to the bezel info file
        png_path: Path to the bezel PNG file

    Returns:
        Tuple containing (img_width, img_height, bz_x, bz_y, bz_width, bz_height, bz_alpha)
    """
    with open(info_path) as bz_info_file:
        bz_info_text = bz_info_file.readlines()

        # Initialize defaults
        img_width, img_height = BezelUtils.fast_image_size(png_path)
        bz_x, bz_y, bz_right, bz_bottom = 0, 0, 0, 0
        bz_alpha = 1.0

        for info_line in bz_info_text:
            if len(info_line) > 7:
                info_line_clean = info_line.replace('"', "").rstrip(",\n").lstrip()
                info_line_data = info_line_clean.split(":")

                if len(info_line_data) < 2:
                    continue

                key = info_line_data[0].lower().strip()
                value = info_line_data[1].strip()

                try:
                    if key == "width":
                        img_width = int(value)
                    elif key == "height":
                        img_height = int(value)
                    elif key == "top":
                        bz_y = int(value)
                    elif key == "left":
                        bz_x = int(value)
                    elif key == "bottom":
                        bz_bottom = int(value)
                    elif key == "right":
                        bz_right = int(value)
                    elif key == "opacity":
                        bz_alpha = float(value)
                except ValueError:
                    # Log error but continue processing
                    logger.warning(f"Invalid value for {key}: {value}")
                    continue

        bz_width = img_width - bz_x - bz_right
        bz_height = img_height - bz_y - bz_bottom

        return img_width, img_height, bz_x, bz_y, bz_width, bz_height, bz_alpha


def _create_standard_layout(
    bz_infos: Dict[str, Any], rom_base: str, tmp_zip_dir: str
) -> Tuple[str, int, int, int, int, int, int, float]:
    """
    Create standard bezel layout from PNG and info file.

    Args:
        bz_infos: Dictionary containing bezel information
        rom_base: Base name of the ROM file
        tmp_zip_dir: Temporary directory for artwork files

    Returns:
        Tuple containing (png_file, img_width, img_height, bz_x, bz_y, bz_width, bz_height, bz_alpha)
    """
    png_file = "default.png"
    _create_symlink(bz_infos["png"], tmp_zip_dir + "/default.png")

    if "info" in bz_infos and os.path.exists(bz_infos["info"]):
        # Parse info file for exact dimensions
        img_width, img_height, bz_x, bz_y, bz_width, bz_height, bz_alpha = (
            _parse_bezel_info_file(bz_infos["info"], bz_infos["png"])
        )
    else:
        # Calculate default dimensions
        img_width, img_height = BezelUtils.fast_image_size(bz_infos["png"])
        try:
            _, _, rotate = getMameMachineSize(rom_base, tmp_zip_dir)
        except Exception:
            rotate = 0

        # Assumes that all bezels are setup for 4:3H or 3:4V aspects
        if rotate in [270, 90]:  # Rotated display
            bz_width = int(img_height * (3 / 4))
        else:
            bz_width = int(img_height * MAINTAIN_ASPECT_RATIO_WIDTH_HEIGHT)

        bz_height = img_height
        bz_x = int((img_width - bz_width) / 2)
        bz_y = 0
        bz_alpha = 1.0

    # Write the layout file
    _write_layout_file(
        tmp_zip_dir,
        png_file,
        bz_x,
        bz_y,
        bz_width,
        bz_height,
        img_width,
        img_height,
        bz_alpha,
    )

    return png_file, img_width, img_height, bz_x, bz_y, bz_width, bz_height, bz_alpha


def _write_layout_file(
    tmp_zip_dir: str,
    png_file: str,
    bz_x: int,
    bz_y: int,
    bz_width: int,
    bz_height: int,
    img_width: int,
    img_height: int,
    bz_alpha: float,
):
    """
    Write the default layout file for MAME.

    Args:
        tmp_zip_dir: Temporary directory for artwork files
        png_file: Name of the PNG file
        bz_x: X coordinate for bezel position
        bz_y: Y coordinate for bezel position
        bz_width: Width of the bezel area
        bz_height: Height of the bezel area
        img_width: Width of the full image
        img_height: Height of the full image
        bz_alpha: Alpha transparency value
    """
    layout_path = tmp_zip_dir + "/default.lay"
    with open(layout_path, "w") as f:
        f.write('<mamelayout version="2">\n')
        f.write('<element name="bezel"><image file="default.png" /></element>\n')
        f.write('<view name="bezel">\n')
        f.write(
            f'<screen index="0"><bounds x="{bz_x}" y="{bz_y}" '
            f'width="{bz_width}" height="{bz_height}" /></screen>\n'
        )
        f.write(
            f'<element ref="bezel"><bounds x="0" y="0" width="{img_width}" '
            f'height="{img_height}" alpha="{bz_alpha}" /></element>\n'
        )
        f.write("</view>\n")
        f.write("</mamelayout>\n")


def _should_apply_tattoo(system: Any) -> bool:
    """
    Check if a tattoo should be applied based on system configuration.

    Args:
        system: System configuration object

    Returns:
        True if tattoo should be applied, False otherwise
    """
    return system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0"


def _apply_tattoo(
    tmp_zip_dir: str, png_file: str, img_width: int, img_height: int, system: Any
) -> str:
    """
    Apply tattoo to the bezel image and return the new file path.

    Args:
        tmp_zip_dir: Temporary directory for artwork files
        png_file: Name of the PNG file to apply tattoo to
        img_width: Width of the image
        img_height: Height of the image
        system: System configuration object

    Returns:
        Path to the new tattooed PNG file
    """
    tattoo = _load_tattoo_image(system)
    if tattoo is None:
        return png_file

    output_png_file = "/tmp/bezel_tattooed.png"
    try:
        back = Image.open(tmp_zip_dir + "/" + png_file)
        tattoo = tattoo.convert("RGBA")
        back = back.convert("RGBA")

        tw, th = BezelUtils.fast_image_size(_get_tattoo_path(system))
        tat_width = int(TATTOO_WIDTH_REFERENCE / DEFAULT_RESOLUTION[0] * img_width)
        percent = float(tat_width / tw)
        tat_height = int(float(th) * percent)

        tattoo = tattoo.resize((tat_width, tat_height), Image.Resampling.BICUBIC)

        # Determine position based on config
        corner = system.config.get("bezel.tattoo_corner", "NW").upper()
        margin = int(TATTOO_VERTICAL_MARGIN / DEFAULT_RESOLUTION[1] * img_height)

        tattoo_canvas = Image.new("RGBA", back.size)
        if corner == "NE":
            tattoo_canvas.paste(tattoo, (img_width - tat_width, margin))
        elif corner == "SE":
            tattoo_canvas.paste(
                tattoo, (img_width - tat_width, img_height - tat_height - margin)
            )
        elif corner == "SW":
            tattoo_canvas.paste(tattoo, (0, img_height - tat_height - margin))
        else:  # NW
            tattoo_canvas.paste(tattoo, (0, margin))

        result = Image.alpha_composite(back, tattoo_canvas)
        result.save(output_png_file, mode="RGBA", format="PNG")
    except Exception as e:
        logger.warning(f"Failed to apply tattoo: {e}")
        # If tattoo fails, return original file
        return png_file

    return output_png_file


def _load_tattoo_image(system: Any) -> Any:
    """
    Load the tattoo image based on system configuration.

    Args:
        system: System configuration object

    Returns:
        Loaded tattoo image or None if not available
    """
    tattoo_config = system.config.get("bezel.tattoo", "generic")
    if tattoo_config == "system":
        tattoo_path = f"/usr/share/reglinux/controller-overlays/{system.name}.png"
        if not os.path.exists(tattoo_path):
            tattoo_path = "/usr/share/reglinux/controller-overlays/generic.png"
    elif tattoo_config == "custom" and os.path.exists(
        system.config.get("bezel.tattoo_file", "")
    ):
        tattoo_path = system.config["bezel.tattoo_file"]
    else:
        tattoo_path = "/usr/share/reglinux/controller-overlays/generic.png"

    if os.path.exists(tattoo_path):
        try:
            return Image.open(tattoo_path)
        except Exception as e:
            logger.warning(f"Error loading tattoo image {tattoo_path}: {e}")
    return None


def _get_tattoo_path(system: Any) -> str:
    """
    Get the path to the tattoo image file.

    Args:
        system: System configuration object

    Returns:
        Path to the tattoo image
    """
    tattoo_config = system.config.get("bezel.tattoo", "generic")
    if tattoo_config == "system":
        tattoo_path = f"/usr/share/reglinux/controller-overlays/{system.name}.png"
        if not os.path.exists(tattoo_path):
            tattoo_path = "/usr/share/reglinux/controller-overlays/generic.png"
    elif tattoo_config == "custom" and os.path.exists(
        system.config.get("bezel.tattoo_file", "")
    ):
        tattoo_path = system.config["bezel.tattoo_file"]
    else:
        tattoo_path = "/usr/share/reglinux/controller-overlays/generic.png"
    return tattoo_path


def _apply_gun_borders(
    tmp_zip_dir: str, png_file: str, borders_size: str, system_config: Dict[str, str]
) -> str:
    """
    Apply gun borders to the bezel image and return the new file path.

    Args:
        tmp_zip_dir: Temporary directory for artwork files
        png_file: Name of the PNG file to apply gun borders to
        borders_size: Size configuration for gun borders
        system_config: System configuration dictionary

    Returns:
        Path to the new bezel file with gun borders
    """
    output_png_file = "/tmp/bezel_gunborders.png"
    inner_size, outer_size = BezelUtils.gun_borders_size(borders_size)
    color = BezelUtils.guns_borders_color_from_config(system_config)

    try:
        BezelUtils.gun_border_image(
            tmp_zip_dir + "/" + png_file,
            output_png_file,
            inner_size,
            outer_size,
            color,
            color,
        )
        return output_png_file
    except Exception as e:
        logger.warning(f"Failed to apply gun borders: {e}")
        # If gun borders fail, return original file
        return png_file


class MameBezelManager(IBezelManager):
    """Bezel manager specific to the MAME emulator."""

    def setup_bezels(
        self, system: Any, rom: str, game_resolution: Dict[str, int], guns: List[Any]
    ) -> None:
        """
        Configure the bezels for a specific game.

        Args:
            system: System configuration object
            rom: Path to the ROM file
            game_resolution: Dictionary containing game resolution (width, height)
            guns: Guns configuration
        """
        # Using default values for parameters not in the interface
        # In a real implementation, these would come from the system configuration
        mess_sys = ""  # Default empty string, could be extracted from system if needed
        setup_mame_bezels(system, rom, mess_sys, game_resolution, guns)
