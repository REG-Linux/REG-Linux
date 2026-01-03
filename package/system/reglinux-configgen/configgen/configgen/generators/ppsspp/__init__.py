"""Ppsspp generator module for REG-Linux
This module handles the generation of ppsspp emulator configurations.
"""

from .ppssppConfig import setPPSSPPConfig
from .ppssppControllers import axisToCode, optionValue, setControllerConfig
from .ppssppGenerator import PPSSPPGenerator

__all__ = [
    "PPSSPPGenerator",
    "axisToCode",
    "optionValue",
    "setControllerConfig",
    "setPPSSPPConfig",
]
