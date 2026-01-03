"""Cgenius generator module for REG-Linux
This module handles the generation of cgenius emulator configurations.
"""

from .cgeniusConfig import setCgeniusConfig
from .cgeniusControllers import setCgeniusControllers
from .cgeniusGenerator import CGeniusGenerator

__all__ = ["CGeniusGenerator", "setCgeniusConfig", "setCgeniusControllers"]
