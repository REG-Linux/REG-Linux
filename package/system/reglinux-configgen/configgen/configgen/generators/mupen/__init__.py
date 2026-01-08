"""Mupen64Plus generator module for REG-Linux.

This module handles the generation of Mupen64Plus emulator configurations.
"""

from .mupenConfig import setMupenConfig
from .mupenGenerator import MupenGenerator

__all__ = ["MupenGenerator", "setMupenConfig"]
