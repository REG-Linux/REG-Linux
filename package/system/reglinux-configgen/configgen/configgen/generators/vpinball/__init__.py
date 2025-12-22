"""
Vpinball generator module for REG-Linux
This module handles the generation of vpinball emulator configurations.
"""

from .vpinballGenerator import VPinballGenerator
from .vpinballConfig import setVpinballConfig

__all__ = ["VPinballGenerator", "setVpinballConfig"]
