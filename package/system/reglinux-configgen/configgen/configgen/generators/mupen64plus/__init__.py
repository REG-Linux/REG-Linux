"""Mupen64Plus generator module for REG-Linux.

This module handles the generation of Mupen64Plus emulator configurations.
"""

from .mupen64plusConfig import setMupen64plusConfig
from .mupen64plusGenerator import Mupen64plusGenerator

__all__ = ["Mupen64plusGenerator", "setMupen64plusConfig"]
