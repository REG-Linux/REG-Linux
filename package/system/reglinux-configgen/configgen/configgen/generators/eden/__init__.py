"""
Eden generator module for REG-Linux
This module handles the generation of eden emulator configurations.
"""

from .edenConfig import setEdenConfig
from .edenController import hatdirectionvalue, setAxis, setButton, setEdenControllers
from .edenGenerator import EdenGenerator

__all__ = ["EdenGenerator", "setEdenConfig", "hatdirectionvalue", "setAxis", "setButton", "setEdenControllers"]
