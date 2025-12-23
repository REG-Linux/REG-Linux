"""
Fallout1 generator module for REG-Linux
This module handles the generation of fallout1 emulator configurations.
"""

from .fallout1Generator import Fallout1Generator
from .fallout1Config import setFalloutConfig
from .fallout1Config import setFalloutIniConfig

__all__ = ["Fallout1Generator", "setFalloutConfig", "setFalloutIniConfig"]
