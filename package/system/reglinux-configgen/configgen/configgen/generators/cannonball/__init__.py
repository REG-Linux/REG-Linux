"""Cannonball generator module for REG-Linux.

This module handles the generation of cannonball emulator configurations.
"""

from . import cannonball_keys
from .cannonballConfig import setCannonballConfig, setSectionConfig
from .cannonballGenerator import CannonballGenerator

__all__ = [
    "CannonballGenerator",
    "setCannonballConfig",
    "setSectionConfig",
    "cannonball_keys",
]
