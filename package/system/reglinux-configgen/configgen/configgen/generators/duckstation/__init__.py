"""Duckstation generator module for REG-Linux.

This module handles the generation of duckstation emulator configurations.
"""

from .duckstationConfig import setDuckstationConfig
from .duckstationControllers import setDuckstationControllers
from .duckstationGenerator import DuckstationGenerator

__all__ = ["DuckstationGenerator", "setDuckstationConfig", "setDuckstationControllers"]
