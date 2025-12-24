"""
Moonlight generator module for REG-Linux
This module handles the generation of moonlight emulator configurations.
"""

from .moonlightConfig import setMoonlightConfig
from .moonlightGenerator import MoonlightGenerator

__all__ = ["MoonlightGenerator", "setMoonlightConfig"]
