"""
Iortcw generator module for REG-Linux
This module handles the generation of iortcw emulator configurations.
"""

from .iortcwConfig import setIortcwConfig
from .iortcwGenerator import IORTCWGenerator

__all__ = ["IORTCWGenerator", "setIortcwConfig"]
