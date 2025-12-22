"""
Moonlight generator module for REG-Linux
This module handles the generation of moonlight emulator configurations.
"""

from .moonlightGenerator import MoonlightGenerator
from .moonlightConfig import setMoonlightConfig

__all__ = ["MoonlightGenerator", "setMoonlightConfig"]
