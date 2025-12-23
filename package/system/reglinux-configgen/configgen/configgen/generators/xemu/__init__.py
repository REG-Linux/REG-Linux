"""
Xemu generator module for REG-Linux
This module handles the generation of xemu emulator configurations.
"""

from .xemuGenerator import XemuGenerator
from .xemuConfig import setXemuConfig

__all__ = ["XemuGenerator", "setXemuConfig"]
