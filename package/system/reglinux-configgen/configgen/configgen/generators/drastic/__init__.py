"""Drastic generator module for REG-Linux.

This module handles the generation of drastic emulator configurations.
"""

from .drasticConfig import setDrasticConfig
from .drasticControllers import setDrasticController
from .drasticGenerator import DrasticGenerator

__all__ = ["DrasticGenerator", "setDrasticConfig", "setDrasticController"]
