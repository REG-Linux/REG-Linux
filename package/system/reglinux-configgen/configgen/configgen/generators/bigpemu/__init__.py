"""
Bigpemu generator module for REG-Linux
This module handles the generation of bigpemu emulator configurations.
"""

from .bigpemuConfig import setBigemuConfig
from .bigpemuGenerator import BigPEmuGenerator

__all__ = ["BigPEmuGenerator", "setBigemuConfig"]
