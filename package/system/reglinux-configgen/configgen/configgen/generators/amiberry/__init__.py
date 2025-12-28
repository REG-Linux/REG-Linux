"""
Amiberry generator module for REG-Linux
This module handles the generation of amiberry emulator configurations.
"""

from .amiberryConfig import setAmiberryConfig
from .amiberryGenerator import AmiberryGenerator

__all__ = ["AmiberryGenerator", "setAmiberryConfig"]
