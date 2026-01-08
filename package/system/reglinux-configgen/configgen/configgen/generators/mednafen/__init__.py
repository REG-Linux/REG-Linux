"""Mednafen generator module for REG-Linux.

This module handles the generation of mednafen emulator configurations.
"""

from .mednafenConfig import setMednafenConfig
from .mednafenControllers import setMednafenControllers
from .mednafenGenerator import MednafenGenerator

__all__ = ["MednafenGenerator", "setMednafenConfig", "setMednafenControllers"]
