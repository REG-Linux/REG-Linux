"""Dolphin generator module for REG-Linux
This module handles the generation of dolphin emulator configurations.
"""

from .dolphinControllers import generateControllerConfig
from .dolphinGenerator import DolphinGenerator

__all__ = ["DolphinGenerator", "generateControllerConfig"]
