# Bare KMS/DRM. No compositor → no window concept.

from pathlib import Path

from .base import Backend


class KmsBackend(Backend):
    name = "kms"
    compositor = ""
    degraded = ("window_exists", "assert_focused", "wait_window_event",
                "move_to_output")

    def __init__(self, present: bool = True):
        if not present:
            self.name = "kms_absent"
        self._card = next(
            (str(p) for p in (Path(f"/dev/dri/card{i}") for i in range(4))
             if p.exists()),
            "",
        )

    def fingerprint(self) -> dict:
        base = super().fingerprint()
        base["kmsdrm_card"] = self._card
        base["dri_driver"] = self._driver()
        return base

    def _driver(self) -> str:
        try:
            with open("/proc/modules") as f:
                txt = f.read()
            for cand in ("amdgpu", "i915", "panfrost", "panthor", "mali",
                         "etnaviv", "vc4", "v3d", "tegra", "msm",
                         "rockchip", "sun4i_drm", "meson_drm"):
                if cand in txt:
                    return cand
        except OSError:
            pass
        return "unknown"
