"""Melonds generator module for REG-Linux.

This module handles the generation of melonds emulator configurations.
"""

from .melondsConfig import setMelonDSConfig
from .melondsControllers import setMelondsControllers
from .melondsGenerator import MelonDSGenerator

__all__ = ["MelonDSGenerator", "setMelonDSConfig", "setMelondsControllers"]
