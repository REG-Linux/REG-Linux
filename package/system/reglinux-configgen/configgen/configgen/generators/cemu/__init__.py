"""Cemu generator module for REG-Linux.

This module handles the generation of cemu emulator configurations.
"""

from .cemuConfig import setCemuConfig, setSectionConfig
from .cemuControllers import setControllerConfig
from .cemuGenerator import CemuGenerator

__all__ = ["CemuGenerator", "setCemuConfig", "setControllerConfig", "setSectionConfig"]
