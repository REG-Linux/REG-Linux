"""Abuse generator module for REG-Linux.

This module handles the generation of abuse emulator configurations.
"""

from . import abuse_keys
from .abuseGenerator import AbuseGenerator

__all__ = ["AbuseGenerator", "abuse_keys"]
