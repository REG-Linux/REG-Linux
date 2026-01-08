"""Pcsx2 generator module for REG-Linux.

This module handles the generation of pcsx2 emulator configurations.
"""

from .pcsx2Config import setPcsx2Config
from .pcsx2Controllers import (
    getWheelType,
    input2wheel,
    isPlayingWithWheel,
    useEmulatorWheels,
)
from .pcsx2Generator import Pcsx2Generator

__all__ = [
    "Pcsx2Generator",
    "getWheelType",
    "input2wheel",
    "isPlayingWithWheel",
    "setPcsx2Config",
    "useEmulatorWheels",
]
