"""
Sonicretro generator module for REG-Linux
This module handles the generation of sonicretro emulator configurations.
"""

from .sonicretroGenerator import SonicRetroGenerator
from .sonicretroConfig import setSonicretroConfig

__all__ = ["SonicRetroGenerator", "setSonicretroConfig"]
