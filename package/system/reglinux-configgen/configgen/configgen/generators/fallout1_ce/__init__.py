"""Fallout1_ce generator module for REG-Linux.

This module handles the generation of fallout1_ce emulator configurations.
"""

from .fallout1_ceConfig import setFalloutConfig, setFalloutIniConfig
from .fallout1_ceGenerator import Fallout1Generator

__all__ = ["Fallout1Generator", "setFalloutConfig", "setFalloutIniConfig"]
