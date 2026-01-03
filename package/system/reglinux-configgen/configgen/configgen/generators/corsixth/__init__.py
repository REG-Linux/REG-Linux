"""Corsixth generator module for REG-Linux
This module handles the generation of corsixth emulator configurations.
"""

from .corsixthConfig import setCorsixthConfig
from .corsixthGenerator import CorsixTHGenerator

__all__ = ["CorsixTHGenerator", "setCorsixthConfig"]
