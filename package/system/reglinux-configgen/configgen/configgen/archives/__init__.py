"""Archives module for REG-Linux ConfigGen.

This module provides utilities for handling archive formats like .zar and .squashfs.
"""

from configgen.archives.squashfs import squashfs_begin, squashfs_end
from configgen.archives.zar import zar_begin, zar_end

__all__ = [
    "squashfs_begin",
    "squashfs_end",
    "zar_begin",
    "zar_end",
]
