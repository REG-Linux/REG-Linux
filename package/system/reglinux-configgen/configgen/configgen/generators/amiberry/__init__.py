"""
Amiberry generator module for REG-Linux
This module handles the generation of amiberry emulator configurations.
"""

from .amiberryGenerator import AmiberryGenerator
from .amiberryConfig import setAmiberryConfig

__all__ = ["AmiberryGenerator", "setAmiberryConfig"]
