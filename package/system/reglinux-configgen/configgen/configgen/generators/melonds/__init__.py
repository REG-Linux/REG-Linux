"""
Melonds generator module for REG-Linux
This module handles the generation of melonds emulator configurations.
"""

from .melondsGenerator import MelonDSGenerator
from .melondsConfig import setMelonDSConfig
from .melondsControllers import *

__all__ = ["MelonDSGenerator", "setMelonDSConfig"]
