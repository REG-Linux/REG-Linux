"""
Cannonball generator module for REG-Linux
This module handles the generation of cannonball emulator configurations.
"""

from .cannonballGenerator import CannonballGenerator
from .cannonballConfig import setCannonballConfig
from .cannonballConfig import setSectionConfig

__all__ = ["CannonballGenerator", "setCannonballConfig", "setSectionConfig"]
