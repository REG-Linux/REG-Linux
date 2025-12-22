"""
Cemu generator module for REG-Linux
This module handles the generation of cemu emulator configurations.
"""

from .cemuGenerator import CemuGenerator
from .cemuConfig import setCemuConfig
from .cemuConfig import setSectionConfig
from .cemuControllers import *

__all__ = ["CemuGenerator", "setCemuConfig", "setSectionConfig"]
