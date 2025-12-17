"""Module that contains the functionalities related to bezels in REG-Linux."""

# Import the main modules to facilitate use
from . import bezel_base
from . import libretro_bezel_manager
from . import mame_bezel_manager

__all__ = [
    "bezel_base",
    "libretro_bezel_manager",
    "mame_bezel_manager",
    "IBezelManager",
    "BezelUtils",
    "LibretroBezelManager",
    "MameBezelManager",
    "clear_bezel_cache",
    "getBezelInfos",
    "fast_image_size",
    "resize_with_fill",
    "resizeImage",
    "padImage",
    "tatooImage",
    "alphaPaste",
    "gun_borders_size",
    "gunBorderImage",
    "gunsBorderSize",
    "gunsBordersColorFomConfig",
    "createTransparentBezel",
    "writeBezelConfig",
    "writeBezelCfgConfig",
    "isLowResolution",
    "setup_mame_bezels",
]

# Import compatibility functions directly
from .bezel_base import (
    clear_bezel_cache,
    getBezelInfos,
    fast_image_size,
    resize_with_fill,
    resizeImage,
    padImage,
    tatooImage,
    alphaPaste,
    gun_borders_size,
    gunBorderImage,
    gunsBorderSize,
    gunsBordersColorFomConfig,
    createTransparentBezel,
)

# Import the classes
from .libretro_bezel_manager import LibretroBezelManager

from .mame_bezel_manager import MameBezelManager

# Import BezelUtils and IBezelManager
from .bezel_base import BezelUtils, IBezelManager

# Import specific functions from libretro_bezel_manager
from .libretro_bezel_manager import (
    writeBezelConfig,
    writeBezelCfgConfig,
    isLowResolution,
)

# Import specific functions from mame_bezel_manager
from .mame_bezel_manager import setup_mame_bezels
