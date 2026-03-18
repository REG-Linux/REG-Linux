"""Azahar generator module for REG-Linux.

This module handles the generation of azahar emulator configurations.
"""

from . import azahar_keys
from .azaharConfig import setAzaharConfig
from .azaharControllers import (
    getMouseMode,
    hatdirectionvalue,
    setAxis,
    setAzaharControllers,
    setButton,
)
from .azaharGenerator import AzaharGenerator

__all__ = [
    "AzaharGenerator",
    "getMouseMode",
    "hatdirectionvalue",
    "setAxis",
    "setAzaharConfig",
    "setAzaharControllers",
    "setButton",
    "azahar_keys",
]
