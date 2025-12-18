"""Module that contains the functionalities related to bezels in REG-Linux."""

# Import the main modules to facilitate use
from . import bezel_base
from . import bezel_common
from . import libretro_bezel_manager
from . import mame_bezel_manager

__all__ = [
    "bezel_base",
    "bezel_common",
    "libretro_bezel_manager",
    "mame_bezel_manager",
    "IBezelManager",
    "BezelUtils",
    "LibretroBezelManager",
    "MameBezelManager",
]

# Import the main classes and utilities
from .bezel_base import BezelUtils, IBezelManager
from .libretro_bezel_manager import LibretroBezelManager
from .mame_bezel_manager import MameBezelManager
