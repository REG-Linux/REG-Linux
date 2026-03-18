"""Sonic2013 generator module for REG-Linux.

This module handles the generation of Sonic2013 emulator configurations.
"""

from .sonic2013Config import setSonic2013Config
from .sonic2013Generator import Sonic2013Generator

__all__ = ["Sonic2013Generator", "setSonic2013Config"]
