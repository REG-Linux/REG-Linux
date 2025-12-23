"""
Fallout2 generator module for REG-Linux
This module handles the generation of fallout2 emulator configurations.
"""

from .fallout2Generator import Fallout2Generator
from .fallout2Config import setFalloutConfig
from .fallout2Config import setFalloutIniConfig

__all__ = ["Fallout2Generator", "setFalloutConfig", "setFalloutIniConfig"]
