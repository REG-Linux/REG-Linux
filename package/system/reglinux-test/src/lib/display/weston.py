# Weston. No scriptable window IPC — only `weston-info` for outputs,
# and `weston-debug` for diagnostics.

import os
import shutil
from pathlib import Path

from ..runner import run
from . import _wl_probe
from .base import Backend


class WestonBackend(Backend):
    name = "weston"
    # window_exists is no longer degraded — served by reglinux-test-wl-probe
    # via ext_foreign_toplevel_list_v1. assert_focused may also be supported
    # via wlr_foreign_toplevel; probed at fingerprint() time.
    degraded = ("assert_focused", "wait_window_event", "move_to_output")

    def window_exists(self, app_id: str):
        return _wl_probe.window_exists(app_id)

    def assert_focused(self, app_id: str) -> tuple[bool | None, str]:
        act = _wl_probe.is_activated(app_id)
        if act is None:
            return None, "degraded"
        return act, "ok"

    def __init__(self):
        self.compositor = self._weston_version()
        self.variant = self._variant()

    def _weston_version(self) -> str:
        r = run(["weston", "--version"], timeout=3)
        if not r.ok():
            return "weston"
        return r.stdout.strip().splitlines()[0] if r.stdout else "weston"

    def _variant(self) -> str:
        # Distinguish optionA (hardkernel) vs optionB (patched) weston builds.
        # Heuristic: presence of marker files placed by the .mk install.
        for marker, label in (
            ("/usr/share/reglinux/weston-variant", None),
            ("/usr/lib/libweston-13/hardkernel", "optionA-hardkernel"),
            ("/usr/lib/libweston-13/patched", "optionB-patched"),
        ):
            p = Path(marker)
            if p.exists():
                try:
                    return label or p.read_text().strip()
                except OSError:
                    return label or "unknown"
        return ""

    def fingerprint(self) -> dict:
        base = super().fingerprint()
        base["compositor_variant"] = self.variant
        base["weston_info"] = self._weston_info_outputs()
        # Probe whether assert_focused is actually supported on this
        # compositor (depends on a foreign-toplevel protocol that exposes
        # activation state, e.g. wlr_foreign_toplevel). Keep the static
        # `degraded` tuple as-is; only adjust the fingerprint's snapshot.
        try:
            supported = _wl_probe.probe_activation_support()
        except Exception:
            supported = False
        if supported and "assert_focused" in base.get("degraded_probes", []):
            base["degraded_probes"] = [
                p for p in base["degraded_probes"] if p != "assert_focused"
            ]
        return base

    def _weston_info_outputs(self) -> list[str]:
        if not shutil.which("weston-info"):
            return []
        r = run(["weston-info"], timeout=5)
        if not r.ok():
            return []
        names = []
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith("name: "):
                names.append(line.split("name: ", 1)[1].strip())
        return names
