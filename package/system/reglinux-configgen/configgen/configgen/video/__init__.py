"""Video module for REG-Linux ConfigGen.

This module provides video mode management and window/compositor control functionality.
"""

from configgen.video.videoMode import (
    changeMode,
    changeMouse,
    getAltDecoration,
    getCurrentMode,
    getCurrentResolution,
    getGLVendor,
    getGLVersion,
    getRefreshRate,
    getScreens,
    getScreensInfos,
    minTomaxResolution,
    supportSystemRotation,
)
from configgen.video.windows_manager import (
    WindowManager,
    start_compositor,
    stop_compositor,
)

__all__ = [
    "changeMode",
    "changeMouse",
    "getCurrentMode",
    "getCurrentResolution",
    "getGLVendor",
    "getGLVersion",
    "getRefreshRate",
    "getScreens",
    "getScreensInfos",
    "minTomaxResolution",
    "supportSystemRotation",
    "getAltDecoration",
    "WindowManager",
    "start_compositor",
    "stop_compositor",
]
