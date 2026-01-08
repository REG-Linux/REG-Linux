"""Mame generator module for REG-Linux.

This module handles the generation of mame emulator configurations.
"""

from .mameControllers import generatePadsConfig
from .mameGenerator import MameGenerator

__all__ = ["MameGenerator", "generatePadsConfig"]
