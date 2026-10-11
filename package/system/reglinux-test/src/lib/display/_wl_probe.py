# Shared helper around the reglinux-test-wl-probe binary.
#
# Returns (status, lines) where status is one of:
#   "ok"               -> lines is the list of per-toplevel dicts
#   "wl_probe_missing" -> binary not installed
#   "no_protocol"      -> compositor doesn't expose foreign-toplevel
#   "error"            -> generic failure (connect, parse, etc.)
#
# Keep this minimal — the C tool does all the protocol work.
#
# Reference:
#   reglinux-test-wl-probe                                   list-once, exit 0
#   reglinux-test-wl-probe --wait <id> -t <sec>              block, exit 2 on timeout
#   reglinux-test-wl-probe --wait-activated <id> -t <sec>    block until activated,
#                                                            exit 2 timeout, exit 3
#                                                            no activation state
#
# Output is one JSON object per line, terminator {"end": true}.

import json
import shutil
from typing import Optional

from ..runner import run

BINARY = "reglinux-test-wl-probe"


def available() -> bool:
    return shutil.which(BINARY) is not None


def list_toplevels(timeout: float = 5.0) -> tuple[str, list[dict]]:
    if not available():
        return "wl_probe_missing", []
    r = run([BINARY], timeout=timeout)
    if r.rc == 127:
        return "wl_probe_missing", []
    if r.rc == 3:
        return "no_protocol", []
    if not r.ok():
        return "error", []
    return _parse(r.stdout)


def wait_for(app_id: str, timeout: float = 10.0) -> tuple[str, list[dict]]:
    if not available():
        return "wl_probe_missing", []
    r = run([BINARY, "--wait", app_id, "--timeout", str(int(timeout))],
            timeout=timeout + 2.0)
    if r.rc == 127:
        return "wl_probe_missing", []
    if r.rc == 2:
        return "timeout", _parse(r.stdout)[1]
    if r.rc == 3:
        return "no_protocol", []
    if not r.ok():
        return "error", []
    return _parse(r.stdout)


def window_exists(app_id: str, timeout: float = 5.0) -> tuple[Optional[bool], str]:
    status, lines = list_toplevels(timeout=timeout)
    if status != "ok":
        return None, status
    for tl in lines:
        if tl.get("app_id") == app_id:
            return True, "ok"
    return False, "ok"


def is_activated(app_id: str, timeout: float = 5.0) -> Optional[bool]:
    """One-shot activation probe.

    Returns:
        True/False if the protocol reports activation for that toplevel,
        None if the toplevel is not present OR the protocol does not
        expose activation state (caller treats None as "unsupported").
    """
    status, lines = list_toplevels(timeout=timeout)
    if status != "ok":
        return None
    for tl in lines:
        if tl.get("app_id") != app_id:
            continue
        act = tl.get("activated")
        # Protocol returned null => unsupported. JSON null -> Python None.
        return act if isinstance(act, bool) else None
    return None


def probe_activation_support() -> bool:
    """Return True iff the compositor exposes activation state.

    Uses --wait-activated with a sentinel app_id and a zero timeout. The
    only relevant signal is exit code 3 (no_activation_state); any other
    outcome — including timeout (exit 2) — means activation IS available
    on the active protocol.
    """
    if not available():
        return False
    r = run([BINARY, "--wait-activated", "__reglinux_probe__", "--timeout", "0"],
            timeout=3.0)
    return r.rc != 3


def wait_activated(app_id: str, timeout: float = 10.0) -> Optional[bool]:
    """Block until app_id is reported activated.

    Returns:
        True   on success (exit 0, matching line emitted),
        False  on timeout (exit 2),
        None   when the protocol does not expose activation state (exit 3)
               or the binary is missing / errored.
    """
    if not available():
        return None
    r = run([BINARY, "--wait-activated", app_id, "--timeout", str(int(timeout))],
            timeout=timeout + 2.0)
    if r.rc == 0:
        return True
    if r.rc == 2:
        return False
    if r.rc == 3:
        return None
    return None


def _parse(stdout: str) -> tuple[str, list[dict]]:
    out: list[dict] = []
    for raw in stdout.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if obj.get("end") is True:
            continue
        if "error" in obj:
            # {"error":"no_protocol_advertised",...}
            return "no_protocol", out
        out.append(obj)
    return "ok", out
