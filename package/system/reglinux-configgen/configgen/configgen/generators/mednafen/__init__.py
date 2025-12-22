"""
Mednafen generator module for REG-Linux
This module handles the generation of mednafen emulator configurations.
"""

from .mednafenGenerator import MednafenGenerator
from .mednafenConfig import setMednafenConfig
from .mednafenControllers import *

__all__ = ["MednafenGenerator", "setMednafenConfig"]
