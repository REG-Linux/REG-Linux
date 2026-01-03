"""Vpinball generator module for REG-Linux
This module handles the generation of vpinball emulator configurations.
"""

from .vpinballConfig import setVpinballConfig
from .vpinballGenerator import VPinballGenerator

__all__ = ["VPinballGenerator", "setVpinballConfig"]
