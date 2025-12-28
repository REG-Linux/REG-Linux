"""
Rpcs3 generator module for REG-Linux
This module handles the generation of rpcs3 emulator configurations.
"""

from .rpcs3Controllers import (
    configure_evdev_controller,
    configure_sdl_controller,
    configure_sony_controller,
    generateControllerConfig,
)
from .rpcs3Generator import Rpcs3Generator

__all__ = [
    "Rpcs3Generator",
    "configure_evdev_controller",
    "configure_sdl_controller",
    "configure_sony_controller",
    "generateControllerConfig",
]
