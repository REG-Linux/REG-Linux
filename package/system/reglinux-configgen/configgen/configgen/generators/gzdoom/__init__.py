"""
Gzdoom generator module for REG-Linux
This module handles the generation of gzdoom emulator configurations.
"""

from .gzdoomGenerator import GZDoomGenerator
from .gzdoomConfig import setGzdoomConfig
from .gzdoomControllers import *

__all__ = ["GZDoomGenerator", "setGzdoomConfig"]
