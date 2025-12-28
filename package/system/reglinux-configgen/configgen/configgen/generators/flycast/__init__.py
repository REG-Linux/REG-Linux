"""
Flycast generator module for REG-Linux
This module handles the generation of flycast emulator configurations.
"""

from .flycastConfig import setFlycastConfig
from .flycastGenerator import FlycastGenerator

__all__ = ["FlycastGenerator", "setFlycastConfig"]
