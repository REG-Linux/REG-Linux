"""
Openbor generator module for REG-Linux
This module handles the generation of openbor emulator configurations.
"""

from .openborGenerator import OpenborGenerator
from .openborControllers import *

__all__ = ["OpenborGenerator"]
