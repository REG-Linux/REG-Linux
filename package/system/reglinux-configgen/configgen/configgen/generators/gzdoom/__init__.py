"""Gzdoom generator module for REG-Linux.

This module handles the generation of gzdoom emulator configurations.
"""

from .gzdoomConfig import setGzdoomConfig
from .gzdoomControllers import setGzdoomControllers
from .gzdoomGenerator import GZDoomGenerator

__all__ = ["GZDoomGenerator", "setGzdoomConfig", "setGzdoomControllers"]
