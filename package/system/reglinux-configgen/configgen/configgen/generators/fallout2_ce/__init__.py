"""Fallout2_ce generator module for REG-Linux.

This module handles the generation of fallout2_ce emulator configurations.
"""

from .fallout2_ceConfig import setFalloutConfig, setFalloutIniConfig
from .fallout2_ceGenerator import Fallout2Generator

__all__ = ["Fallout2Generator", "setFalloutConfig", "setFalloutIniConfig"]
