"""
Duckstation generator module for REG-Linux
This module handles the generation of duckstation emulator configurations.
"""

from .duckstationGenerator import DuckstationGenerator
from .duckstationConfig import setDuckstationConfig
from .duckstationControllers import *

__all__ = ["DuckstationGenerator", "setDuckstationConfig"]
