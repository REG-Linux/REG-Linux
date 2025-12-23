"""
Flycast generator module for REG-Linux
This module handles the generation of flycast emulator configurations.
"""

from .flycastGenerator import FlycastGenerator
from .flycastConfig import setFlycastConfig

__all__ = ["FlycastGenerator", "setFlycastConfig"]
