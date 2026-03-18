"""Core module for REG-Linux ConfigGen.

This module contains the fundamental domain objects used throughout the system.
"""

from configgen.core.command import Command
from configgen.core.emulator import Emulator
from configgen.core.exceptions import (
    BezelImageError,
    BIOSNotFoundError,
    ConfigGenError,
    EmulatorNotFoundError,
    ExternalScriptError,
    FileMissingError,
    GeneratorError,
    ImageProcessingError,
    MachineNotFoundError,
    TattooImageError,
)

__all__ = [
    "Command",
    "Emulator",
    "ConfigGenError",
    "EmulatorNotFoundError",
    "BIOSNotFoundError",
    "MachineNotFoundError",
    "GeneratorError",
    "FileMissingError",
    "ImageProcessingError",
    "TattooImageError",
    "BezelImageError",
    "ExternalScriptError",
]
