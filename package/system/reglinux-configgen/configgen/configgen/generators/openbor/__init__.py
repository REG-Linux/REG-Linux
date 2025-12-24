"""
Openbor generator module for REG-Linux
This module handles the generation of openbor emulator configurations.
"""

from .openborControllers import JoystickValue, setControllerConfig, setupControllers
from .openborGenerator import OpenborGenerator

__all__ = [
    "OpenborGenerator",
    "JoystickValue",
    "setControllerConfig",
    "setupControllers",
]
