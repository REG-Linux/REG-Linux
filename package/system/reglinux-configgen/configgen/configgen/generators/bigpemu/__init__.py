"""
Bigpemu generator module for REG-Linux
This module handles the generation of bigpemu emulator configurations.
"""

from .bigpemuGenerator import BigPEmuGenerator
from .bigpemuConfig import setBigemuConfig

__all__ = ["BigPEmuGenerator", "setBigemuConfig"]
