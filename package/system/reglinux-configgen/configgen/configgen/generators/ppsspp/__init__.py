"""
Ppsspp generator module for REG-Linux
This module handles the generation of ppsspp emulator configurations.
"""

from .ppssppGenerator import PPSSPPGenerator
from .ppssppConfig import setPPSSPPConfig
from .ppssppControllers import *

__all__ = ["PPSSPPGenerator", "setPPSSPPConfig"]
