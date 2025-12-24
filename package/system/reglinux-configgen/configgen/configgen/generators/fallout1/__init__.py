"""
Fallout1 generator module for REG-Linux
This module handles the generation of fallout1 emulator configurations.
"""

from .fallout1Config import setFalloutConfig, setFalloutIniConfig
from .fallout1Generator import Fallout1Generator

__all__ = ["Fallout1Generator", "setFalloutConfig", "setFalloutIniConfig"]
