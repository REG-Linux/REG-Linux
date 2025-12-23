"""
Cgenius generator module for REG-Linux
This module handles the generation of cgenius emulator configurations.
"""

from .cgeniusGenerator import CGeniusGenerator
from .cgeniusConfig import setCgeniusConfig
from .cgeniusControllers import *

__all__ = ["CGeniusGenerator", "setCgeniusConfig"]
