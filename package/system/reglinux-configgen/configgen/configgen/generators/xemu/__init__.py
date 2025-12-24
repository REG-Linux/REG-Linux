"""
Xemu generator module for REG-Linux
This module handles the generation of xemu emulator configurations.
"""

from .xemuConfig import setXemuConfig
from .xemuGenerator import XemuGenerator

__all__ = ["XemuGenerator", "setXemuConfig"]
