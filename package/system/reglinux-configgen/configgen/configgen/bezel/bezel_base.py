"""
Module that defines the interfaces and base classes for the bezel system in REG-Linux.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image as ImageType
from configgen.systemFiles import OVERLAY_USER, OVERLAY_SYSTEM
from configgen.utils.videoMode import getAltDecoration
from configgen.utils.logger import get_logger
import struct
import hashlib
import os
import glob
import shutil

eslog = get_logger(__name__)

# Constants
BEZEL_CACHE_DIR = Path("/tmp/bezel_cache")
if not BEZEL_CACHE_DIR.exists():
    BEZEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_RESOLUTION = (1920, 1080)


class IBezelManager(ABC):
    """Interface for emulator-specific bezel managers."""

    @abstractmethod
    def setup_bezels(self, system, rom, game_resolution: Dict[str, int], guns) -> None:
        """Configure the bezels for a specific game."""
        pass


class BezelUtils:
    """Utility class with helper functions for bezel manipulation."""

    @staticmethod
    def generate_cache_key(*args) -> str:
        """
        Generate a unique cache key based on input parameters.

        Args:
            *args: Variable arguments to create the key string

        Returns:
            str: MD5 hash of the arguments
        """
        key_str = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    @staticmethod
    def get_cached_image(cache_key: str) -> Optional[str]:
        """
        Retrieve cached image if it exists.

        Args:
            cache_key: The key for the cached image

        Returns:
            Path to cached image if exists, else None
        """
        cached_path = BEZEL_CACHE_DIR / f"{cache_key}.png"
        if cached_path.exists():
            return str(cached_path)
        return None

    @staticmethod
    def save_to_cache(image_path: str, cache_key: str) -> None:
        """
        Save an image to the cache.

        Args:
            image_path: Path to the image to cache
            cache_key: The key for the cached image
        """
        cached_path = BEZEL_CACHE_DIR / f"{cache_key}.png"
        shutil.copy2(image_path, str(cached_path))

    @staticmethod
    def clear_bezel_cache() -> None:
        """
        Clear all cached bezel images to free up space.
        """
        files = glob.glob(str(BEZEL_CACHE_DIR / "*.png"))
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass  # Ignore errors when removing cached files

    @staticmethod
    def get_bezel_infos(
        rom: str, bezel: str, system_name: str, emulator: str
    ) -> Optional[Dict[str, str]]:
        """
        Locate the appropriate bezel overlay image and related files based on
        ROM name, system name, and emulator used.

        The search follows a prioritized list:
        1. Game-specific user/system overlays
        2. System-specific overlays (with optional alternative decoration)
        3. Default overlays (fallback)

        Args:
            rom: Path to the ROM file
            bezel: Name of the bezel set to use
            system_name: Name of the system
            emulator: Name of the emulator

        Returns:
            Dictionary containing paths to bezel files and metadata, or None if not found
        """
        alt_decoration = getAltDecoration(system_name, rom, emulator)
        rom_base = Path(rom).stem

        candidates = []

        # Priority: game-specific overlays
        candidates += [
            ("games", OVERLAY_USER, True, f"{system_name}/{rom_base}"),
            ("games", OVERLAY_SYSTEM, True, f"{system_name}/{rom_base}"),
            ("games", OVERLAY_USER, True, rom_base),
            ("games", OVERLAY_SYSTEM, True, rom_base),
        ]

        # System-specific overlays (with or without altDecoration)
        if alt_decoration != 0:
            candidates.append(
                ("systems", OVERLAY_USER, False, f"{system_name}-{alt_decoration}")
            )
        candidates.append(("systems", OVERLAY_USER, False, system_name))
        if alt_decoration != 0:
            candidates.append(
                ("systems", OVERLAY_SYSTEM, False, f"{system_name}-{alt_decoration}")
            )
        candidates.append(("systems", OVERLAY_SYSTEM, False, system_name))

        # Default fallback overlays
        if alt_decoration != 0:
            candidates.append(("", OVERLAY_USER, True, f"default-{alt_decoration}"))
        candidates.append(("", OVERLAY_USER, True, "default"))
        if alt_decoration != 0:
            candidates.append(("", OVERLAY_SYSTEM, True, f"default-{alt_decoration}"))
        candidates.append(("", OVERLAY_SYSTEM, True, "default"))

        for subfolder, basepath, bezel_game, name in candidates:
            prefix = (
                f"{basepath}/{bezel}/{subfolder}/"
                if subfolder
                else f"{basepath}/{bezel}/"
            )
            overlay_png_file = f"{prefix}{name}.png"
            if Path(overlay_png_file).exists():
                eslog.debug(f"Original bezel file used: {overlay_png_file}")
                return {
                    "png": overlay_png_file,
                    "info": f"{prefix}{name}.info",
                    "layout": f"{prefix}{name}.lay",
                    "mamezip": f"{prefix}{name}.zip",
                    "specific_to_game": bezel_game,
                }

        return None

    @staticmethod
    def fast_image_size(image_file: str) -> Tuple[int, int]:
        """
        Return the size (width, height) of a PNG image by reading its header.
        Much faster than using PIL.Image.open().size.

        Args:
            image_file: Path to the PNG image file

        Returns:
            Tuple with (width, height) of the image, or (-1, -1) if error
        """
        img_path = Path(image_file)
        if not img_path.exists():
            return -1, -1
        try:
            with img_path.open("rb") as fhandle:
                head = fhandle.read(32)
                if len(head) != 32 or struct.unpack(">i", head[4:8])[0] != 0x0D0A1A0A:
                    return -1, -1
                return struct.unpack(">ii", head[16:24])
        except (OSError, struct.error):
            return -1, -1

    @staticmethod
    def resize_with_fill(
        img: "ImageType",
        target_size: Tuple[int, int],
        stretch: bool = False,
        fillcolor: str = "black",
    ) -> "ImageType":
        """
        Resize an image with padding or stretching.

        Args:
            img: Source image
            target_size: Desired size as (width, height)
            stretch: Whether to stretch instead of pad
            fillcolor: Background color to use

        Returns:
            The resized image
        """
        from PIL import ImageOps

        if stretch:
            return ImageOps.fit(img, target_size)

        return ImageOps.pad(img, target_size, color=fillcolor, centering=(0.5, 0.5))

    @staticmethod
    def resize_image(
        input_png: str,
        output_png: str,
        screen_width: int,
        screen_height: int,
        bezel_stretch: bool = False,
    ) -> None:
        """
        Resize a bezel image to match screen size, maintaining alpha if needed.

        Args:
            input_png: Input PNG file path
            output_png: Output PNG file path
            screen_width: Screen width
            screen_height: Screen height
            bezel_stretch: Whether to stretch the bezel

        Raises:
            ValueError: If input or output path is None or empty
            FileNotFoundError: If input image does not exist
            IOError: If there's an error opening or saving the image
        """
        # Validate input parameters
        if not input_png or not output_png:
            eslog.error("Input or output path is None or empty")
            raise ValueError("Input or output path is None or empty")

        # Validate input file exists
        input_path = Path(input_png)
        if not input_path.exists():
            eslog.error(f"Input image does not exist: {input_png}")
            raise FileNotFoundError(f"Input image does not exist: {input_png}")

        # Generate cache key based on input parameters
        cache_key = BezelUtils.generate_cache_key(
            "resize", input_png, screen_width, screen_height, bezel_stretch
        )

        # Check if image is already cached
        cached_path = BezelUtils.get_cached_image(cache_key)
        if cached_path:
            eslog.debug(f"Using cached resized bezel: {cached_path}")
            # Copy cached image to output location
            try:
                shutil.copy2(cached_path, output_png)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied copying cached bezel from {cached_path} to {output_png}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(
                    f"OS error copying cached bezel from {cached_path} to {output_png}: {e}"
                )
                raise
            return

        # Create output directory if it doesn't exist
        output_path = Path(output_png)
        output_dir = output_path.parent
        if output_dir and not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied creating output directory {output_dir}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(f"OS error creating output directory {output_dir}: {e}")
                raise

        try:
            imgin = Image.open(input_png)
        except (IOError, OSError, Image.UnidentifiedImageError) as e:
            eslog.error(f"Error opening input image {input_png}: {e}")
            raise

        from PIL import ImageOps

        fillcolor = "black"
        eslog.debug(f"Resizing bezel: image mode {imgin.mode}")
        if imgin.mode != "RGBA":
            try:
                BezelUtils.alpha_paste(
                    input_png,
                    output_png,
                    imgin,
                    fillcolor,
                    (screen_width, screen_height),
                    bezel_stretch,
                )
            except Exception as e:
                eslog.error(f"Error in alpha paste operation for {input_png}: {e}")
                raise
        else:
            try:
                imgout = BezelUtils.resize_with_fill(
                    imgin,
                    (screen_width, screen_height),
                    stretch=bezel_stretch,
                    fillcolor=fillcolor,
                )
                imgout.save(output_png, mode="RGBA", format="PNG")
            except (IOError, OSError) as e:
                eslog.error(f"Error saving output image {output_png}: {e}")
                raise

        # Save the result to cache
        try:
            BezelUtils.save_to_cache(output_png, cache_key)
        except Exception as e:
            eslog.warning(f"Failed to save bezel to cache: {e}")
            # Continue execution even if cache save fails

    @staticmethod
    def pad_image(
        input_png: str,
        output_png: str,
        screen_width: int,
        screen_height: int,
        bezel_width: int,
        bezel_height: int,
        bezel_stretch: bool = False,
    ) -> None:
        """
        Pad the bezel image to match screen size.

        Args:
            input_png: Input PNG file path
            output_png: Output PNG file path
            screen_width: Screen width
            screen_height: Screen height
            bezel_width: Bezel width
            bezel_height: Bezel height
            bezel_stretch: Whether to stretch the bezel

        Raises:
            ValueError: If input or output path is None or empty
            FileNotFoundError: If input image does not exist
            IOError: If there's an error opening or saving the image
        """
        # Validate input parameters
        if not input_png or not output_png:
            eslog.error("Input or output path is None or empty")
            raise ValueError("Input or output path is None or empty")

        # Validate input file exists
        input_path = Path(input_png)
        if not input_path.exists():
            eslog.error(f"Input image does not exist: {input_png}")
            raise FileNotFoundError(f"Input image does not exist: {input_png}")

        # Create output directory if it doesn't exist
        output_path = Path(output_png)
        output_dir = output_path.parent
        if output_dir and not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied creating output directory {output_dir}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(f"OS error creating output directory {output_dir}: {e}")
                raise

        try:
            imgin = Image.open(input_png)
        except (IOError, OSError, Image.UnidentifiedImageError) as e:
            eslog.error(f"Error opening input image {input_png}: {e}")
            raise

        from PIL import ImageOps

        fillcolor = "black"
        eslog.debug(f"Padding bezel: image mode {imgin.mode}")
        if imgin.mode != "RGBA":
            try:
                BezelUtils.alpha_paste(
                    input_png,
                    output_png,
                    imgin,
                    fillcolor,
                    (screen_width, screen_height),
                    bezel_stretch,
                )
            except Exception as e:
                eslog.error(f"Error in alpha paste operation for {input_png}: {e}")
                raise
        else:
            try:
                imgout = BezelUtils.resize_with_fill(
                    imgin,
                    (screen_width, screen_height),
                    stretch=bezel_stretch,
                    fillcolor=fillcolor,
                )
                imgout.save(output_png, mode="RGBA", format="PNG")
            except (IOError, OSError) as e:
                eslog.error(f"Error saving output image {output_png}: {e}")
                raise

    @staticmethod
    def tattoo_image(input_png: str, output_png: str, system) -> None:
        """
        Overlay a controller image ("tattoo") on top of the bezel, depending on system config.

        Args:
            input_png: Input PNG file path
            output_png: Output PNG file path
            system: System configuration object

        Raises:
            ValueError: If input or output path is None or empty
            FileNotFoundError: If input image does not exist
            IOError: If there's an error opening or saving the image
        """
        # Validate input parameters
        if not input_png or not output_png:
            eslog.error("Input or output path is None or empty")
            raise ValueError("Input or output path is None or empty")

        # Validate input file exists
        input_path = Path(input_png)
        if not input_path.exists():
            eslog.error(f"Input image does not exist: {input_png}")
            raise FileNotFoundError(f"Input image does not exist: {input_png}")

        # Create output directory if it doesn't exist
        output_path = Path(output_png)
        output_dir = output_path.parent
        if output_dir and not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied creating output directory {output_dir}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(f"OS error creating output directory {output_dir}: {e}")
                raise

        # Generate cache key based on input parameters
        tattoo_config = system.config.get("bezel.tattoo", "generic")
        tattoo_file = None
        if tattoo_config == "system":
            tattoo_file = f"/usr/share/reglinux/controller-overlays/{system.name}.png"
            if not Path(tattoo_file).exists():
                tattoo_file = "/usr/share/reglinux/controller-overlays/generic.png"
        elif (
            tattoo_config == "custom"
            and Path(system.config.get("bezel.tattoo_file", "")).exists()
        ):
            tattoo_file = system.config["bezel.tattoo_file"]
        else:
            tattoo_file = "/usr/share/reglinux/controller-overlays/generic.png"

        cache_key = BezelUtils.generate_cache_key(
            "tattoo",
            input_png,
            tattoo_file,
            system.config.get("bezel.resize_tattoo", "default"),
            system.config.get("bezel.tattoo_corner", "NW"),
            BezelUtils.fast_image_size(
                input_png
            ),  # Include input image size in cache key
        )

        # Check if image is already cached
        cached_path = BezelUtils.get_cached_image(cache_key)
        if cached_path:
            eslog.debug(f"Using cached tattooed bezel: {cached_path}")
            # Copy cached image to output location
            try:
                shutil.copy2(cached_path, output_png)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied copying cached tattooed bezel from {cached_path} to {output_png}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(
                    f"OS error copying cached tattooed bezel from {cached_path} to {output_png}: {e}"
                )
                raise
            return

        tattoo = None
        try:
            if system.config["bezel.tattoo"] == "system":
                tattoo_file = (
                    f"/usr/share/reglinux/controller-overlays/{system.name}.png"
                )
                if not Path(tattoo_file).exists():
                    tattoo_file = "/usr/share/reglinux/controller-overlays/generic.png"
                tattoo = Image.open(tattoo_file)
            elif (
                system.config["bezel.tattoo"] == "custom"
                and Path(system.config["bezel.tattoo_file"]).exists()
            ):
                tattoo_file = system.config["bezel.tattoo_file"]
                tattoo = Image.open(tattoo_file)
            else:
                tattoo_file = "/usr/share/reglinux/controller-overlays/generic.png"
                tattoo = Image.open(tattoo_file)
        except (IOError, OSError, Image.UnidentifiedImageError) as e:
            eslog.error(f"Error opening tattoo image: {tattoo_file} - {str(e)}")
            raise

        back = Image.open(input_png).convert("RGBA")
        tattoo = tattoo.convert("RGBA") if tattoo else None

        if not tattoo:
            eslog.error("Tattoo image could not be loaded, skipping tattoo overlay.")
            raise Exception("Tattoo image could not be loaded")

        w, h = BezelUtils.fast_image_size(input_png)
        tw, th = BezelUtils.fast_image_size(tattoo_file)

        if system.config.get("bezel.resize_tattoo") == 0:
            if tw > w or th > h:
                pcent = float(w / tw)
                th = int(th * pcent)
                tattoo = tattoo.resize((w, th), Image.Resampling.BICUBIC)
        else:
            twtemp = int((225 / 1920) * w)
            pcent = float(twtemp / tw)
            th = int(th * pcent)
            tattoo = tattoo.resize((twtemp, th), Image.Resampling.BICUBIC)
            tw = twtemp

        margin = int((20 / 1080) * h)
        corner = system.config.get("bezel.tattoo_corner", "NW").upper()

        tattoo_canvas = Image.new("RGBA", back.size)
        if corner == "NE":
            tattoo_canvas.paste(tattoo, (w - tw, margin))
        elif corner == "SE":
            tattoo_canvas.paste(tattoo, (w - tw, h - th - margin))
        elif corner == "SW":
            tattoo_canvas.paste(tattoo, (0, h - th - margin))
        else:
            tattoo_canvas.paste(tattoo, (0, margin))

        back = Image.alpha_composite(back, tattoo_canvas)
        imgnew = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        imgnew.paste(back, (0, 0, w, h))
        try:
            imgnew.save(output_png, mode="RGBA", format="PNG")
        except (IOError, OSError) as e:
            eslog.error(f"Error saving tattooed output image {output_png}: {e}")
            raise

        # Save the result to cache
        try:
            BezelUtils.save_to_cache(output_png, cache_key)
        except Exception as e:
            eslog.warning(f"Failed to save tattooed bezel to cache: {e}")
            # Continue execution even if cache save fails

    @staticmethod
    def alpha_paste(
        input_png: str,
        output_png: str,
        imgin: "ImageType",
        fillcolor: str,
        screensize: Tuple[int, int],
        bezel_stretch: bool,
    ) -> None:
        """
        Paste the alpha channel from an image into a resized canvas.
        Handles non-RGBA images and crops to match aspect ratio.

        Args:
            input_png: Input PNG file path
            output_png: Output PNG file path
            imgin: Input image object
            fillcolor: Fill color for the canvas
            screensize: Screen size as (width, height)
            bezel_stretch: Whether to stretch the bezel

        Raises:
            ValueError: If input or output path is None or empty
            FileNotFoundError: If input image does not exist
            Exception: If image has no transparency channel
            IOError: If there's an error saving the image
        """
        # Validate input parameters
        if not input_png or not output_png:
            eslog.error("Input or output path is None or empty")
            raise ValueError("Input or output path is None or empty")

        # Validate input file exists
        input_path = Path(input_png)
        if not input_path.exists():
            eslog.error(f"Input image does not exist: {input_png}")
            raise FileNotFoundError(f"Input image does not exist: {input_png}")

        # Create output directory if it doesn't exist
        output_path = Path(output_png)
        output_dir = output_path.parent
        if output_dir and not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied creating output directory {output_dir}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(f"OS error creating output directory {output_dir}: {e}")
                raise

        if "transparency" not in imgin.info:
            eslog.error(f"Input image {input_png} has no transparency channel")
            raise Exception("no transparent pixels in the image, abort")

        alpha = imgin.split()[-1]
        ix, iy = BezelUtils.fast_image_size(input_png)
        sx, sy = screensize
        i_ratio = float(ix) / float(iy)
        s_ratio = float(sx) / float(sy)

        if i_ratio - s_ratio > 0.01:
            new_x = int(ix * s_ratio / i_ratio)
            delta = int(ix - new_x)
            alpha = alpha.crop((delta // 2, 0, new_x + delta // 2, iy))
            ix = new_x

        imgnew = Image.new("RGBA", (ix, iy), (0, 0, 0, 255))
        imgnew.paste(alpha, (0, 0, ix, iy))
        try:
            imgout = BezelUtils.resize_with_fill(
                imgnew, screensize, stretch=bezel_stretch, fillcolor=fillcolor
            )
            imgout.save(output_png, mode="RGBA", format="PNG")
        except (IOError, OSError) as e:
            eslog.error(f"Error saving alpha pasted output image {output_png}: {e}")
            raise

    @staticmethod
    def gun_borders_size(borders_size: str) -> Tuple[int, int]:
        """
        Return preset values for gun border sizes depending on text config.

        Args:
            borders_size: Text configuration for border size

        Returns:
            Tuple with inner and outer border sizes
        """
        if borders_size == "thin":
            return 1, 0
        if borders_size == "medium":
            return 2, 0
        if borders_size == "big":
            return 2, 1
        return 0, 0

    @staticmethod
    def gun_border_image(
        input_png: str,
        output_png: str,
        inner_border_size_per: int = 2,
        outer_border_size_per: int = 3,
        inner_border_color: str = "#ffffff",
        outer_border_color: str = "#000000",
    ) -> int:
        """
        Draws outer and inner borders on the bezel image for lightgun detection.

        Args:
            input_png: Input PNG file path
            output_png: Output PNG file path
            inner_border_size_per: Inner border size as percentage
            outer_border_size_per: Outer border size as percentage
            inner_border_color: Color for inner border
            outer_border_color: Color for outer border

        Returns:
            Combined border size

        Raises:
            ValueError: If input or output path is None or empty
            FileNotFoundError: If input image does not exist
            IOError: If there's an error saving the image
        """
        # Validate input parameters
        if not input_png or not output_png:
            eslog.error("Input or output path is None or empty")
            raise ValueError("Input or output path is None or empty")

        # Validate input file exists
        input_path = Path(input_png)
        if not input_path.exists():
            eslog.error(f"Input image does not exist: {input_png}")
            raise FileNotFoundError(f"Input image does not exist: {input_png}")

        # Create output directory if it doesn't exist
        output_path = Path(output_png)
        output_dir = output_path.parent
        if output_dir and not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied creating output directory {output_dir}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(f"OS error creating output directory {output_dir}: {e}")
                raise

        # Generate cache key based on input parameters
        cache_key = BezelUtils.generate_cache_key(
            "gunborder",
            input_png,
            inner_border_size_per,
            outer_border_size_per,
            inner_border_color,
            outer_border_color,
            BezelUtils.fast_image_size(input_png),
        )

        # Check if image is already cached
        cached_path = BezelUtils.get_cached_image(cache_key)
        if cached_path:
            eslog.debug(f"Using cached bezel with gun borders: {cached_path}")
            # Copy cached image to output location
            try:
                shutil.copy2(cached_path, output_png)
            except PermissionError as e:
                eslog.error(
                    f"Permission denied copying cached gun border bezel from {cached_path} to {output_png}: {e}"
                )
                raise
            except OSError as e:
                eslog.error(
                    f"OS error copying cached gun border bezel from {cached_path} to {output_png}: {e}"
                )
                raise
            w, h = BezelUtils.fast_image_size(input_png)
            outer_border_size = max(1, h * outer_border_size_per // 100)
            inner_border_size = max(1, w * inner_border_size_per // 100)
            return outer_border_size + inner_border_size

        from PIL import ImageDraw

        w, h = BezelUtils.fast_image_size(input_png)
        if w <= 0 or h <= 0:
            eslog.error(f"Invalid image dimensions for {input_png}: {w}x{h}")
            raise ValueError(f"Invalid image dimensions for {input_png}: {w}x{h}")

        outer_border_size = max(1, h * outer_border_size_per // 100)
        outer_shapes = [
            [(0, 0), (w, outer_border_size)],
            [(w - outer_border_size, 0), (w, h)],
            [(0, h - outer_border_size), (w, h)],
            [(0, 0), (outer_border_size, h)],
        ]

        inner_border_size = max(1, w * inner_border_size_per // 100)
        inner_shapes = [
            [
                (outer_border_size, outer_border_size),
                (w - outer_border_size, outer_border_size + inner_border_size),
            ],
            [
                (w - outer_border_size - inner_border_size, outer_border_size),
                (w - outer_border_size, h - outer_border_size),
            ],
            [
                (outer_border_size, h - outer_border_size - inner_border_size),
                (w - outer_border_size, h - outer_border_size),
            ],
            [
                (outer_border_size, outer_border_size),
                (outer_border_size + inner_border_size, h - outer_border_size),
            ],
        ]

        try:
            back = Image.open(input_png)
        except (IOError, OSError, Image.UnidentifiedImageError) as e:
            eslog.error(f"Error opening input image {input_png}: {e}")
            raise

        imgnew = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        imgnew.paste(back, (0, 0, w, h))
        draw = ImageDraw.Draw(imgnew)

        for shape in outer_shapes:
            draw.rectangle(shape, fill=outer_border_color)
        for shape in inner_shapes:
            draw.rectangle(shape, fill=inner_border_color)

        try:
            imgnew.save(output_png, mode="RGBA", format="PNG")
        except (IOError, OSError) as e:
            eslog.error(f"Error saving gun border image {output_png}: {e}")
            raise

        # Save the result to cache
        try:
            BezelUtils.save_to_cache(output_png, cache_key)
        except Exception as e:
            eslog.warning(f"Failed to save gun border bezel to cache: {e}")
            # Continue execution even if cache save fails

        return outer_border_size + inner_border_size

    @staticmethod
    def guns_border_size(
        w: int, h: int, inner_border_size_per: int = 2, outer_border_size_per: int = 3
    ) -> int:
        """
        Calculate combined border height used for lightgun overlay.

        Args:
            w: Width
            h: Height
            inner_border_size_per: Inner border size as percentage
            outer_border_size_per: Outer border size as percentage

        Returns:
            Combined border size
        """
        return (h * (inner_border_size_per + outer_border_size_per)) // 100

    @staticmethod
    def guns_borders_color_from_config(config: Dict[str, str]) -> str:
        """
        Return hex color for gun borders from config string.

        Args:
            config: Configuration dictionary

        Returns:
            Hex color string
        """
        color_key = config.get("controllers.guns.borderscolor")
        if color_key is None:
            return "#ffffff"  # default color
        return {
            "red": "#ff0000",
            "green": "#00ff00",
            "blue": "#0000ff",
            "white": "#ffffff",
        }.get(color_key, "#ffffff")

    @staticmethod
    def create_transparent_bezel(output_png: str, width: int, height: int) -> None:
        """
        Create a fully transparent bezel PNG of given size.

        Args:
            output_png: Output PNG file path
            width: Width of the bezel
            height: Height of the bezel
        """
        imgnew = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        imgnew.save(output_png, mode="RGBA", format="PNG")


# Compatibility functions to maintain legacy APIs
def clear_bezel_cache() -> None:
    """
    Clear all cached bezel images to free up space.
    """
    BezelUtils.clear_bezel_cache()


def getBezelInfos(
    rom: str, bezel: str, systemName: str, emulator: str
) -> Optional[Dict[str, str]]:
    """
    Locate the appropriate bezel overlay image and related files based on
    ROM name, system name, and emulator used.

    The search follows a prioritized list:
    1. Game-specific user/system overlays
    2. System-specific overlays (with optional alternative decoration)
    3. Default overlays (fallback)

    Args:
        rom: Path to the ROM file
        bezel: Name of the bezel set to use
        systemName: Name of the system
        emulator: Name of the emulator

    Returns:
        Dictionary containing paths to bezel files and metadata, or None if not found
    """
    return BezelUtils.get_bezel_infos(rom, bezel, systemName, emulator)


def fast_image_size(image_file: str) -> Tuple[int, int]:
    """
    Return the size (width, height) of a PNG image by reading its header.
    Much faster than using PIL.Image.open().size.

    Args:
        image_file: Path to the PNG image file

    Returns:
        Tuple with (width, height) of the image, or (-1, -1) if error
    """
    return BezelUtils.fast_image_size(image_file)


def resize_with_fill(
    img: "ImageType",
    target_size: Tuple[int, int],
    stretch: bool = False,
    fillcolor: str = "black",
) -> "ImageType":
    """
    Resize an image with padding or stretching.

    Args:
        img: Source image
        target_size: Desired size as (width, height)
        stretch: Whether to stretch instead of pad
        fillcolor: Background color to use

    Returns:
        The resized image
    """
    return BezelUtils.resize_with_fill(img, target_size, stretch, fillcolor)


def resizeImage(
    input_png: str,
    output_png: str,
    screen_width: int,
    screen_height: int,
    bezel_stretch: bool = False,
) -> None:
    """
    Resize a bezel image to match screen size, maintaining alpha if needed.

    Args:
        input_png: Input PNG file path
        output_png: Output PNG file path
        screen_width: Screen width
        screen_height: Screen height
        bezel_stretch: Whether to stretch the bezel

    Raises:
        ValueError: If input or output path is None or empty
        FileNotFoundError: If input image does not exist
        IOError: If there's an error opening or saving the image
    """
    BezelUtils.resize_image(
        input_png, output_png, screen_width, screen_height, bezel_stretch
    )


def padImage(
    input_png: str,
    output_png: str,
    screen_width: int,
    screen_height: int,
    bezel_width: int,
    bezel_height: int,
    bezel_stretch: bool = False,
) -> None:
    """
    Pad the bezel image to match screen size.

    Args:
        input_png: Input PNG file path
        output_png: Output PNG file path
        screen_width: Screen width
        screen_height: Screen height
        bezel_width: Bezel width
        bezel_height: Bezel height
        bezel_stretch: Whether to stretch the bezel

    Raises:
        ValueError: If input or output path is None or empty
        FileNotFoundError: If input image does not exist
        IOError: If there's an error opening or saving the image
    """
    BezelUtils.pad_image(
        input_png,
        output_png,
        screen_width,
        screen_height,
        bezel_width,
        bezel_height,
        bezel_stretch,
    )


def tatooImage(input_png: str, output_png: str, system) -> None:
    """
    Overlay a controller image ("tattoo") on top of the bezel, depending on system config.

    Args:
        input_png: Input PNG file path
        output_png: Output PNG file path
        system: System configuration object

    Raises:
        ValueError: If input or output path is None or empty
        FileNotFoundError: If input image does not exist
        IOError: If there's an error opening or saving the image
    """
    BezelUtils.tattoo_image(input_png, output_png, system)


def alphaPaste(
    input_png: str,
    output_png: str,
    imgin: "ImageType",
    fillcolor: str,
    screensize: Tuple[int, int],
    bezel_stretch: bool,
) -> None:
    """
    Paste the alpha channel from an image into a resized canvas.
    Handles non-RGBA images and crops to match aspect ratio.

    Args:
        input_png: Input PNG file path
        output_png: Output PNG file path
        imgin: Input image object
        fillcolor: Fill color for the canvas
        screensize: Screen size as (width, height)
        bezel_stretch: Whether to stretch the bezel

    Raises:
        ValueError: If input or output path is None or empty
        FileNotFoundError: If input image does not exist
        Exception: If image has no transparency channel
        IOError: If there's an error saving the image
    """
    BezelUtils.alpha_paste(
        input_png, output_png, imgin, fillcolor, screensize, bezel_stretch
    )


def gun_borders_size(borders_size: str) -> Tuple[int, int]:
    """
    Return preset values for gun border sizes depending on text config.

    Args:
        borders_size: Text configuration for border size

    Returns:
        Tuple with inner and outer border sizes
    """
    return BezelUtils.gun_borders_size(borders_size)


def gunBorderImage(
    input_png: str,
    output_png: str,
    innerBorderSizePer: int = 2,
    outerBorderSizePer: int = 3,
    innerBorderColor: str = "#ffffff",
    outerBorderColor: str = "#000000",
) -> int:
    """
    Draws outer and inner borders on the bezel image for lightgun detection.

    Args:
        input_png: Input PNG file path
        output_png: Output PNG file path
        innerBorderSizePer: Inner border size as percentage
        outerBorderSizePer: Outer border size as percentage
        innerBorderColor: Color for inner border
        outerBorderColor: Color for outer border

    Returns:
        Combined border size

    Raises:
        ValueError: If input or output path is None or empty
        FileNotFoundError: If input image does not exist
        IOError: If there's an error saving the image
    """
    return BezelUtils.gun_border_image(
        input_png,
        output_png,
        innerBorderSizePer,
        outerBorderSizePer,
        innerBorderColor,
        outerBorderColor,
    )


def gunsBorderSize(
    w: int, h: int, innerBorderSizePer: int = 2, outerBorderSizePer: int = 3
) -> int:
    """
    Calculate combined border height used for lightgun overlay.

    Args:
        w: Width
        h: Height
        innerBorderSizePer: Inner border size as percentage
        outerBorderSizePer: Outer border size as percentage

    Returns:
        Combined border size
    """
    return BezelUtils.guns_border_size(w, h, innerBorderSizePer, outerBorderSizePer)


def gunsBordersColorFomConfig(config: Dict[str, str]) -> str:
    """
    Return hex color for gun borders from config string.

    Args:
        config: Configuration dictionary

    Returns:
        Hex color string
    """
    return BezelUtils.guns_borders_color_from_config(config)


def createTransparentBezel(output_png: str, width: int, height: int) -> None:
    """
    Create a fully transparent bezel PNG of given size.

    Args:
        output_png: Output PNG file path
        width: Width of the bezel
        height: Height of the bezel
    """
    BezelUtils.create_transparent_bezel(output_png, width, height)
