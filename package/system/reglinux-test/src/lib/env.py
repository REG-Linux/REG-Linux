# Detect board, arch, display backend. Snapshot at run start.

import os
import platform
import shutil
from pathlib import Path

from .runner import run
from .display import detect as detect_display


def build_env() -> dict:
    return {
        "board": _board(),
        "arch": platform.machine(),
        "kernel": platform.release(),
        "release_info": _release_info(),
        "regmsg": _regmsg_version(),
        "regstation_binary": shutil.which("regstation"),
        "libra_test_binary": shutil.which("libra_test"),
        "display": detect_display().fingerprint(),
        "free_mem_mb": _free_mem_mb(),
        "userdata_free_mb": _disk_free_mb("/userdata"),
        "env_vars": _selected_env(),
    }


def _board() -> str:
    for p in ("/boot/boot/reglinux-boot.conf",
              "/etc/reglinux-release",
              "/boot/reglinux-boot.conf"):
        if Path(p).exists():
            try:
                txt = Path(p).read_text()
                for line in txt.splitlines():
                    if line.startswith("BOARD=") or line.startswith("board="):
                        return line.split("=", 1)[1].strip().strip('"')
            except OSError:
                pass
    return os.environ.get("BOARD", "unknown")


def _release_info() -> dict:
    info = {}
    p = Path("/etc/reglinux-release")
    if p.exists():
        try:
            for line in p.read_text().splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    info[k.strip()] = v.strip().strip('"')
        except OSError:
            pass
    return info


def _regmsg_version() -> dict:
    r = run(["regmsg", "--version"], timeout=5)
    return {
        "available": r.ok(),
        "raw": r.stdout.strip() if r.ok() else r.stderr.strip(),
    }


def _free_mem_mb() -> int | None:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except OSError:
        return None
    return None


def _disk_free_mb(path: str) -> int | None:
    try:
        st = os.statvfs(path)
        return (st.f_bavail * st.f_frsize) // (1024 * 1024)
    except OSError:
        return None


def _selected_env() -> dict:
    keys = ("WAYLAND_DISPLAY", "XDG_SESSION_TYPE", "DISPLAY",
            "XDG_RUNTIME_DIR", "SWAYSOCK", "WESTON_CONFIG_FILE")
    return {k: os.environ.get(k, "") for k in keys}
