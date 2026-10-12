# Abstract display backend. Methods that are not natively available
# must return (None, "degraded") so the engine can route to a fallback.

from typing import Iterable

from .. import ipc, probe


class Backend:
    name: str = "abstract"
    compositor: str = ""
    degraded: tuple[str, ...] = ()  # capabilities NOT natively supported

    # -------- universal probes (work on all backends) --------

    def screenshot(self, path: str) -> bool:
        return probe.screenshot(path)

    def is_process_alive(self, process_name: str) -> bool:
        return probe.is_process_alive(process_name)

    def wait_visible(self, process_name: str, screenshot_path: str,
                     timeout: float = 30.0) -> dict:
        return probe.wait_visible(process_name, screenshot_path, timeout)

    def outputs(self) -> list[str]:
        return ipc.screen_listoutputs()

    def current_output(self) -> str:
        return ipc.screen_getoutput()

    def modes(self, output: str | None = None) -> list[str]:
        return ipc.screen_listmodes(output)

    def rotation(self, output: str | None = None) -> str:
        return ipc.screen_getrotation(output)

    # -------- compositor-specific (optional) --------

    def window_exists(self, app_id: str) -> tuple[bool | None, str]:
        return None, "degraded"

    def assert_focused(self, app_id: str) -> tuple[bool | None, str]:
        return None, "degraded"

    def xwayland_active(self) -> bool:
        return probe.is_process_alive("Xwayland")

    # -------- fingerprint --------

    def fingerprint(self) -> dict:
        return {
            "backend": self.name,
            "compositor": self.compositor,
            "outputs": self._outputs_detail(),
            "xwayland_active": self.xwayland_active(),
            "degraded_probes": list(self.degraded),
        }

    def _outputs_detail(self) -> list[dict]:
        out = []
        for name in self.outputs():
            modes = self.modes(name)
            out.append({
                "name": name,
                "modes_count": len(modes),
                "rotation": self.rotation(name),
            })
        return out
