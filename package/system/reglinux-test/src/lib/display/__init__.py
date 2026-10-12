# Display-backend detection. Priority: sway > weston > generic wayland > kms.

import os
import shutil
from pathlib import Path

from .base import Backend
from .kms import KmsBackend
from .sway import SwayBackend
from .wayland_generic import WaylandGenericBackend
from .weston import WestonBackend


def detect() -> Backend:
    wl = os.environ.get("WAYLAND_DISPLAY", "")
    if wl:
        if _sway_alive():
            return SwayBackend()
        if _weston_alive():
            return WestonBackend()
        return WaylandGenericBackend()
    if _kms_present():
        return KmsBackend()
    # Last resort: KMS backend with degraded markers.
    return KmsBackend(present=False)


def _sway_alive() -> bool:
    if not shutil.which("swaymsg"):
        return False
    from ..runner import run
    return run(["swaymsg", "-t", "get_version"], timeout=3).ok()


def _weston_alive() -> bool:
    from ..runner import run
    return run(["pgrep", "-x", "weston"], timeout=3).ok()


def _kms_present() -> bool:
    return any(Path(f"/dev/dri/card{i}").exists() for i in range(4))
