"""
Mupen64Plus generator module for REG-Linux
This module handles the generation of Mupen64Plus emulator configurations.
"""

from .mupenGenerator import MupenGenerator
from .mupenConfig import setMupenConfig

__all__ = ["MupenGenerator", "setMupenConfig"]
