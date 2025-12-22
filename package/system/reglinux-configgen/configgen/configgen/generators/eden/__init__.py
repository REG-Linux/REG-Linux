"""
Eden generator module for REG-Linux
This module handles the generation of eden emulator configurations.
"""

from .edenGenerator import EdenGenerator
from .edenConfig import setEdenConfig
from .edenController import *

__all__ = ["EdenGenerator", "setEdenConfig"]
