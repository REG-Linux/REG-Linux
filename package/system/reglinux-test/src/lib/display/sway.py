# Sway / wlroots compositor. Rich IPC.

import json
import os
import shutil
import signal
import subprocess
import time

from ..runner import run
from .base import Backend


class SwayBackend(Backend):
    name = "sway"
    degraded: tuple[str, ...] = ()

    def __init__(self):
        self.compositor = self._sway_version()
        self.swaymsg = shutil.which("swaymsg") or "swaymsg"

    def _sway_version(self) -> str:
        r = run(["swaymsg", "-t", "get_version"], timeout=3)
        if not r.ok():
            return "sway"
        try:
            obj = json.loads(r.stdout)
            return f"sway {obj.get('human_readable', '?')}"
        except json.JSONDecodeError:
            return "sway"

    def _get_tree(self) -> dict | None:
        r = run([self.swaymsg, "-t", "get_tree"], timeout=5)
        if not r.ok():
            return None
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            return None

    def window_exists(self, app_id: str) -> tuple[bool | None, str]:
        tree = self._get_tree()
        if tree is None:
            return None, "tree_unavailable"
        return _walk_match(tree, app_id), "ok"

    def assert_focused(self, app_id: str) -> tuple[bool | None, str]:
        tree = self._get_tree()
        if tree is None:
            return None, "tree_unavailable"
        return _walk_focused(tree, app_id), "ok"

    def wait_window_event(self, app_id: str, change: str = "new",
                          timeout: float = 30.0) -> dict:
        """Block until sway emits a window event matching app_id+change.
        Fast path used by wait_visible override below."""
        argv = [self.swaymsg, "-t", "subscribe", "-m", '["window"]']
        try:
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, text=True,
                                    preexec_fn=os.setsid)
        except (FileNotFoundError, PermissionError) as e:
            return {"matched": False, "error": str(e)}

        deadline = time.time() + timeout
        matched = False
        info: dict = {}
        try:
            while time.time() < deadline:
                proc.stdout.flush() if proc.stdout else None
                line = proc.stdout.readline() if proc.stdout else ""
                if not line:
                    time.sleep(0.05)
                    if proc.poll() is not None:
                        break
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("change") != change:
                    continue
                c = obj.get("container", {})
                wp = c.get("window_properties") or {}
                if c.get("app_id") == app_id or wp.get("class") == app_id \
                        or wp.get("instance") == app_id:
                    matched = True
                    info = {
                        "app_id": c.get("app_id"),
                        "name": c.get("name"),
                        "pid": c.get("pid"),
                        "change": change,
                    }
                    break
        finally:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass
        return {"matched": matched, "info": info}

    def wait_visible(self, process_name: str, screenshot_path: str,
                     timeout: float = 30.0) -> dict:
        """Sway override: use subscribe for low-latency window detection,
        then a single screenshot to confirm a non-black frame."""
        started = time.time()
        ev = self.wait_window_event(process_name, change="new", timeout=timeout)
        if not ev["matched"]:
            # fall back to common polling path
            return super().wait_visible(process_name, screenshot_path, timeout)
        from .. import probe
        if probe.screenshot(screenshot_path):
            ok, _ = probe.assert_not_black(screenshot_path)
        else:
            ok = False
        return {
            "visible": ok,
            "pid": ev["info"].get("pid"),
            "first_frame_ms": int((time.time() - started) * 1000),
            "via": "sway_subscribe",
        }


def _walk_match(node: dict, app_id: str) -> bool:
    if node.get("app_id") == app_id:
        return True
    wp = node.get("window_properties") or {}
    if wp.get("class") == app_id or wp.get("instance") == app_id:
        return True
    for child in (node.get("nodes") or []) + (node.get("floating_nodes") or []):
        if _walk_match(child, app_id):
            return True
    return False


def _walk_focused(node: dict, app_id: str) -> bool:
    if node.get("focused") and (
        node.get("app_id") == app_id
        or (node.get("window_properties") or {}).get("class") == app_id
    ):
        return True
    for child in (node.get("nodes") or []) + (node.get("floating_nodes") or []):
        if _walk_focused(child, app_id):
            return True
    return False
