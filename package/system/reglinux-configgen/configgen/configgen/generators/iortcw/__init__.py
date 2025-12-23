"""
Iortcw generator module for REG-Linux
This module handles the generation of iortcw emulator configurations.
"""

from .iortcwGenerator import IORTCWGenerator
from .iortcwConfig import setIortcwConfig

__all__ = ["IORTCWGenerator", "setIortcwConfig"]
