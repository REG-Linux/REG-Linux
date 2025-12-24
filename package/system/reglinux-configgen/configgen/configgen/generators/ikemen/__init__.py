"""
Ikemen generator module for REG-Linux
This module handles the generation of ikemen emulator configurations.
"""

from .ikemenControllers import Joymapping, Keymapping
from .ikemenGenerator import IkemenGenerator

__all__ = ["IkemenGenerator", "Joymapping", "Keymapping"]
