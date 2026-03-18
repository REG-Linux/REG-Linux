"""Controllers utils module for REG-Linux ConfigGen.

This module provides utility functions for special input devices like guns and racing wheels,
as well as general controller utilities.
"""

import re
from pathlib import Path
from typing import Any

from configgen.controllers.utils.gunsUtils import (
    precalibration,
    precalibration_copyDir,
    precalibration_copyFile,
    precalibration_copyFilesInDir,
)
from configgen.controllers.utils.wheelsUtils import (
    get_wheels_from_device_infos,
    reconfigure_angle_rotation,
    reconfigure_controllers,
    reset_controllers,
)


def shortNameFromPath(path_name: str) -> str:
    """Extract a short name from a file path."""
    redname = Path(path_name).stem.lower()
    inpar = False
    inblock = False
    ret = ""
    for c in redname:
        if (
            not inpar
            and not inblock
            and ((c >= "a" and c <= "z") or (c >= "0" and c <= "9"))
        ):
            ret += c
        elif c == "(":
            inpar = True
        elif c == ")":
            inpar = False
        elif c == "[" or c == "]":
            inblock = True
    return ret


def dev2int(dev: str) -> Any:
    """Convert a device path to its integer event ID."""
    matches = re.match(r"^/dev/input/event([0-9]*)$", dev)
    if matches is None:
        return None
    return int(matches.group(1))


__all__ = [
    "dev2int",
    "get_wheels_from_device_infos",
    "precalibration",
    "precalibration_copyFile",
    "precalibration_copyDir",
    "precalibration_copyFilesInDir",
    "reconfigure_angle_rotation",
    "reconfigure_controllers",
    "reset_controllers",
    "shortNameFromPath",
]
