"""Sonicretro generator module for REG-Linux
This module handles the generation of sonicretro emulator configurations.
"""

from .sonicretroConfig import setSonicretroConfig
from .sonicretroGenerator import SonicRetroGenerator

__all__ = ["SonicRetroGenerator", "setSonicretroConfig"]
