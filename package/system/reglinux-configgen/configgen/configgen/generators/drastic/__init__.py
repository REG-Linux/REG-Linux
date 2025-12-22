"""
Drastic generator module for REG-Linux
This module handles the generation of drastic emulator configurations.
"""

from .drasticGenerator import DrasticGenerator
from .drasticConfig import setDrasticConfig
from .drasticControllers import *

__all__ = ["DrasticGenerator", "setDrasticConfig"]
