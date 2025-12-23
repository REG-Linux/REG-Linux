"""
Pcsx2 generator module for REG-Linux
This module handles the generation of pcsx2 emulator configurations.
"""

from .pcsx2Generator import Pcsx2Generator
from .pcsx2Config import setPcsx2Config
from .pcsx2Controllers import *

__all__ = ["Pcsx2Generator", "setPcsx2Config"]
