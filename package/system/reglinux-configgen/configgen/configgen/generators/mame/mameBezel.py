import os
import shutil
from typing import Dict, Optional, Tuple
from PIL import Image
from xml.dom import minidom
from subprocess import Popen, PIPE

from configgen.utils.bezels import (
    getBezelInfos,
    createTransparentBezel,
    gun_borders_size,
    gunBorderImage,
    gunsBordersColorFomConfig,
    fast_image_size,
)
from configgen.utils.logger import get_logger

logger = get_logger(__name__)

# Constants
MAINTAIN_ASPECT_RATIO_WIDTH_HEIGHT = 4 / 3  # Assumption for bezel aspect ratio
TATTOO_WIDTH_REFERENCE = 240  # Half the difference between 4:3 and 16:9 on 1920px
TATTOO_VERTICAL_MARGIN = 20  # Vertical margin for tattoo placement
DEFAULT_RESOLUTION = (1920, 1080)  # Fallback resolution


def setup_mame_bezels(system, rom, messSys: str, game_resolution: Dict[str, int], guns):
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


def _extract_bezel_set(system) -> Optional[str]:
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


def _get_guns_borders_size(guns, system_config) -> Optional[str]:
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
    system,
    rom,
    messSys,
    game_resolution: Dict[str, int],
    guns_borders_size: Optional[str],
):
    """Create MAME artwork configuration for bezels."""
    tmp_zip_dir: Optional[str] = None  # Initialize to None
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
                createTransparentBezel(
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


def _get_bezel_info(bezel_set: Optional[str], system, rom) -> Optional[Dict]:
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
            return getBezelInfos(rom, bezel_set, system.name, "mame")
        except Exception as e:
            logger.warning(f"Error getting bezel info for {rom}: {e}")
            return None
    return None


def _safe_file_operation(operation_func, *args, **kwargs):
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


def _ensure_valid_image_dimensions(
    img_width: Optional[int],
    img_height: Optional[int],
    default_resolution: Tuple[int, int] = DEFAULT_RESOLUTION,
) -> Tuple[int, int]:
    """
    Ensure image dimensions are valid, using defaults if needed.

    Args:
        img_width: Width of the image (may be None)
        img_height: Height of the image (may be None)
        default_resolution: Default (width, height) to return if values are None

    Returns:
        Valid image dimensions as (width, height) tuple
    """
    if img_width is None or img_height is None:
        return default_resolution
    return img_width, img_height


def _process_bezel_layout(
    bz_infos: Dict, rom_base: str, mess_sys: str, tmp_zip_dir: str
) -> Optional[Tuple]:
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
        img_width, img_height = fast_image_size(bz_infos["png"])
        # Return minimal defaults since exact positions not needed for layout
        return png_file, img_width, img_height, 0, 0, img_width, img_height, 1.0

    # Handle standard PNG + info file case
    return _create_standard_layout(bz_infos, rom_base, tmp_zip_dir)


def _handle_mamezip_case(rom_base: str, mess_sys: str, bz_infos: Dict):
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
) -> Tuple[int, int, int, int, int, int, float]:
    """
    Parse bezel info file and return position and size values.

    Args:
        info_path: Path to the bezel info file
        png_path: Path to the bezel PNG file

    Returns:
        Tuple containing (img_width, img_height, bz_x, bz_y, bz_width, bz_height, bz_alpha)
    """
    with open(info_path, "r") as bz_info_file:
        bz_info_text = bz_info_file.readlines()

        # Initialize defaults
        img_width, img_height = fast_image_size(png_path)
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
    bz_infos: Dict, rom_base: str, tmp_zip_dir: str
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
        img_width, img_height = fast_image_size(bz_infos["png"])
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


def _should_apply_tattoo(system) -> bool:
    """
    Check if a tattoo should be applied based on system configuration.

    Args:
        system: System configuration object

    Returns:
        True if tattoo should be applied, False otherwise
    """
    return system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0"


def _apply_tattoo(
    tmp_zip_dir: str, png_file: str, img_width: int, img_height: int, system
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

        tw, th = fast_image_size(_get_tattoo_path(system))
        tat_width = int(TATTOO_WIDTH_REFERENCE / DEFAULT_RESOLUTION[0] * img_width)
        percent = float(tat_width / tw)
        tat_height = int(float(th) * percent)

        # Use Image.Resampling.LANCZOS for antialiasing (ANTIALIAS is deprecated)
        resample_filter = Image.Resampling.LANCZOS
        tattoo = tattoo.resize((tat_width, tat_height), resample_filter)
        alpha_tat = tattoo.split()[-1]

        # Determine position based on config
        corner = _get_tattoo_corner(system)
        pos_x, pos_y = _calculate_tattoo_position(
            corner, img_width, img_height, tat_width, tat_height
        )

        back.paste(tattoo, (pos_x, pos_y), alpha_tat)
        img_new = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 255))
        img_new.paste(back, (0, 0, img_width, img_height))
        img_new.save(output_png_file, format="PNG")

        try:
            os.remove(tmp_zip_dir + "/" + png_file)
        except OSError:
            pass
        _create_symlink(output_png_file, tmp_zip_dir + "/" + png_file)
    except Exception as e:
        logger.error(f"Error applying tattoo: {e}")
        return png_file

    return png_file


def _load_tattoo_image(system) -> Optional[Image.Image]:
    """
    Load the tattoo image based on system configuration.

    Args:
        system: System configuration object

    Returns:
        Loaded tattoo image if successful, otherwise None
    """
    tattoo_path = _get_tattoo_path(system)
    try:
        return Image.open(tattoo_path)
    except Exception as e:
        logger.error(f"Error opening tattoo file: {tattoo_path}, Error: {e}")
        return None


def _get_tattoo_path(system) -> str:
    """
    Get the path for the tattoo image based on system configuration.

    Args:
        system: System configuration object

    Returns:
        Path to the tattoo image file
    """
    if system.config["bezel.tattoo"] == "system":
        tattoo_path = f"/usr/share/reglinux/controller-overlays/{system.name}.png"
        if not os.path.exists(tattoo_path):
            tattoo_path = "/usr/share/reglinux/controller-overlays/generic.png"
    elif system.config["bezel.tattoo"] == "custom" and os.path.exists(
        system.config["bezel.tattoo_file"]
    ):
        tattoo_path = system.config["bezel.tattoo_file"]
    else:
        tattoo_path = "/usr/share/reglinux/controller-overlays/generic.png"
    return tattoo_path


def _get_tattoo_corner(system) -> str:
    """
    Get the tattoo corner from system config or return default.

    Args:
        system: System configuration object

    Returns:
        Tattoo corner identifier (NW, NE, SW, SE)
    """
    if system.isOptSet("bezel.tattoo_corner"):
        return system.config["bezel.tattoo_corner"]
    else:
        return "NW"


def _calculate_tattoo_position(
    corner: str, img_width: int, img_height: int, tat_width: int, tat_height: int
) -> Tuple[int, int]:
    """
    Calculate the position for the tattoo based on the corner setting.

    Args:
        corner: Corner identifier (NW, NE, SW, SE)
        img_width: Width of the base image
        img_height: Height of the base image
        tat_width: Width of the tattoo image
        tat_height: Height of the tattoo image

    Returns:
        Tuple of (x, y) position for the tattoo
    """
    corner_upper = corner.upper()
    if corner_upper == "NE":
        pos_x = img_width - tat_width
        pos_y = TATTOO_VERTICAL_MARGIN
    elif corner_upper == "SE":
        pos_x = img_width - tat_width
        pos_y = img_height - tat_height - TATTOO_VERTICAL_MARGIN
    elif corner_upper == "SW":
        pos_x = 0
        pos_y = img_height - tat_height - TATTOO_VERTICAL_MARGIN
    else:  # default = NW
        pos_x = 0
        pos_y = TATTOO_VERTICAL_MARGIN
    return pos_x, pos_y


def _apply_gun_borders(
    tmp_zip_dir: str, png_file: str, guns_borders_size: str, system_config: Dict
) -> str:
    """
    Apply gun borders to the bezel image and return the new file path.

    Args:
        tmp_zip_dir: Temporary directory for artwork files
        png_file: Name of the PNG file to apply gun borders to
        guns_borders_size: Size identifier for gun borders
        system_config: System configuration dictionary

    Returns:
        Path to the new gun-borders PNG file
    """
    output_png_file = "/tmp/bezel_gunborders.png"
    try:
        inner_size, outer_size = gun_borders_size(guns_borders_size)
        gunBorderImage(
            tmp_zip_dir + "/" + png_file,
            output_png_file,
            inner_size,
            outer_size,
            gunsBordersColorFomConfig(system_config),
        )

        try:
            os.remove(tmp_zip_dir + "/" + png_file)
        except OSError:
            pass
        _create_symlink(output_png_file, tmp_zip_dir + "/" + png_file)
    except Exception as e:
        logger.error(f"Error applying gun borders: {e}")
        return png_file

    return png_file


def getMameMachineSize(machine: str, tmpdir: str) -> Tuple[int, int, int]:
    """
    Get the machine display size information from MAME.

    Args:
        machine: Name of the MAME machine/ROM
        tmpdir: Temporary directory for XML output

    Returns:
        Tuple of (width, height, rotation) of the display

    Raises:
        Exception: If MAME command fails or display element is not found
    """
    infofile: Optional[str] = None  # Initialize infofile to None
    try:
        proc = Popen(
            ["/usr/bin/mame/mame", "-listxml", machine], stdout=PIPE, stderr=PIPE
        )
        out, err = proc.communicate()
        exitcode = proc.returncode

        if exitcode != 0:
            raise Exception(
                f"MAME -listxml {machine} failed with exit code {exitcode}. Error: {err.decode()}"
            )

        infofile = os.path.join(tmpdir, "infxml")
        with open(infofile, "w", encoding="utf-8") as f:
            f.write(out.decode())

        infos = minidom.parse(infofile)
        displays = infos.getElementsByTagName("display")

        for element in displays:
            iwidth = element.getAttribute("width")
            iheight = element.getAttribute("height")
            irotate = element.getAttribute("rotate")

            if iwidth and iheight and irotate:  # Ensure values are not empty
                return int(iwidth), int(iheight), int(irotate)

        raise Exception("Display element not found or missing required attributes")
    finally:
        # Clean up the temporary file
        if infofile is not None:  # Check if infofile was successfully assigned
            try:
                os.remove(infofile)
            except OSError:
                # File may not have been created due to an earlier error
                pass
