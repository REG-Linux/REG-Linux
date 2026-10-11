# Wayland session detected but compositor unknown. window_exists is served
# by reglinux-test-wl-probe whenever the compositor exposes a foreign-toplevel
# protocol; assert_focused works only when the protocol exposes activation
# state (wlr_foreign_toplevel); everything else stays degraded.

from . import _wl_probe
from .base import Backend


class WaylandGenericBackend(Backend):
    name = "wayland_generic"
    compositor = "wayland (unknown compositor)"
    degraded = ("assert_focused", "wait_window_event", "move_to_output")

    def window_exists(self, app_id: str):
        return _wl_probe.window_exists(app_id)

    def assert_focused(self, app_id: str) -> tuple[bool | None, str]:
        act = _wl_probe.is_activated(app_id)
        if act is None:
            return None, "degraded"
        return act, "ok"

    def fingerprint(self) -> dict:
        base = super().fingerprint()
        # Drop assert_focused from the fingerprint's degraded list when the
        # underlying protocol probe reports activation support. Keep the
        # static `degraded` tuple unchanged — callers that read it at class
        # level still see the conservative default.
        try:
            supported = _wl_probe.probe_activation_support()
        except Exception:
            supported = False
        if supported and "assert_focused" in base.get("degraded_probes", []):
            base["degraded_probes"] = [
                p for p in base["degraded_probes"] if p != "assert_focused"
            ]
        return base
