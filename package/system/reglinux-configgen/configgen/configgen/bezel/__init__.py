"""Module that contains the functionalities related to bezels in REG-Linux."""

# Import the main modules to facilitate use
from . import bezel_base, bezel_common, libretro_bezel_manager, mame_bezel_manager

__all__ = [
    "BezelUtils",
    "IBezelManager",
    "LibretroBezelManager",
    "MameBezelManager",
    "bezel_base",
    "bezel_common",
    "libretro_bezel_manager",
    "mame_bezel_manager",
]

# Import the main classes and utilities
from .bezel_base import BezelUtils, IBezelManager
from .libretro_bezel_manager import LibretroBezelManager
from .mame_bezel_manager import MameBezelManager
