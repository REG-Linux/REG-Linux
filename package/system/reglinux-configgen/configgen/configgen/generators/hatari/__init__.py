"""Hatari generator module for REG-Linux
This module handles the generation of hatari emulator configurations.
"""

from .hatariControllers import setHatariControllers
from .hatariGenerator import HatariGenerator

__all__ = ["HatariGenerator", "setHatariControllers"]
