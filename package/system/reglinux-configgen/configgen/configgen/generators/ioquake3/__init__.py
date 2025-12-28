"""
Ioquake3 generator module for REG-Linux
This module handles the generation of ioquake3 emulator configurations.
"""

from .ioquake3Config import setIoquake3Config
from .ioquake3Generator import IOQuake3Generator

__all__ = ["IOQuake3Generator", "setIoquake3Config"]
