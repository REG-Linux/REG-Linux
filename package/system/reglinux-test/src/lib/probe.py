# Cross-backend probes. Uses subprocess only.

import os
import shutil
import time
from pathlib import Path

from . import ipc
from .runner import run

# regmsg writes timestamped screenshots here (daemon config
# DEFAULT_SCREENSHOT_DIR). The CLI cannot specify a path.
_REGMSG_SHOT_DIR = "/userdata/screenshots"


def pgrep(name: str) -> list[int]:
    r = run(["pgrep", "-x", name], timeout=5)
    if not r.ok():
        return []
    return [int(x) for x in r.stdout.split() if x.strip().isdigit()]


def is_process_alive(name: str) -> bool:
    return bool(pgrep(name))


def kill_orphans(patterns: list[str]) -> dict:
    """Check which patterns currently have a running process.
    Matches the process basename (argv[0]) exactly, NOT the full cmdline.
    Short names like 'sh' or 'play' would otherwise spuriously match every
    shell or chromium worker on the system."""
    found = {}
    for p in patterns:
        # -x: exact match on comm (process name, max 15 chars by kernel).
        # We pass the basename; pgrep handles truncation tolerance.
        r = run(["pgrep", "-x", p], timeout=5)
        if r.ok() and r.stdout.strip():
            # Resolve full cmdline of each pid for context.
            pids = [pid for pid in r.stdout.split() if pid.strip().isdigit()]
            cmdlines = []
            for pid in pids:
                try:
                    with open(f"/proc/{pid}/cmdline", "rb") as f:
                        cmd = f.read().replace(b"\x00", b" ").decode(
                            "utf-8", "replace").strip()
                except OSError:
                    cmd = pid
                cmdlines.append(f"{pid} {cmd}")
            found[p] = cmdlines
    return found


def proc_rss_mb(pid: int) -> float | None:
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    kb = int(line.split()[1])
                    return round(kb / 1024.0, 1)
    except (OSError, ValueError):
        return None
    return None


def screenshot(path: str) -> bool:
    """Capture a screenshot to an exact path.

    grim (Wayland) takes an explicit output path, so prefer it when a
    Wayland session is present. regmsg's `screen getscreenshot` cannot —
    the daemon writes its own timestamped file under /userdata/screenshots
    — so the regmsg fallback runs the command then moves the newest file.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("grim"):
        r = run(["grim", path], timeout=10)
        if r.ok() and Path(path).exists() and Path(path).stat().st_size > 0:
            return True

    # Fallback: regmsg getscreenshot, then locate the file it produced.
    before = _shot_dir_snapshot()
    r = ipc.screen_screenshot()
    if not r.ok():
        return False
    newest = _newest_new_shot(before)
    if newest is None:
        return False
    try:
        shutil.move(str(newest), path)
    except OSError:
        return False
    return Path(path).exists() and Path(path).stat().st_size > 0


def _shot_dir_snapshot() -> set:
    try:
        return set(os.listdir(_REGMSG_SHOT_DIR))
    except OSError:
        return set()


def _newest_new_shot(before: set) -> Path | None:
    try:
        added = [Path(_REGMSG_SHOT_DIR) / n
                 for n in os.listdir(_REGMSG_SHOT_DIR) if n not in before]
    except OSError:
        return None
    added = [p for p in added if p.is_file()]
    if not added:
        return None
    return max(added, key=lambda p: p.stat().st_mtime)


def png_mean_luma(path: str) -> float | None:
    """Mean luma 0..255 of a PNG, decoded with zlib + sw bilinear sampling.
    Tries Pillow first if installed, else manual decode. Returns None on failure."""
    try:
        from PIL import Image  # type: ignore
        with Image.open(path) as im:
            im = im.convert("L")
            w, h = im.size
            cx0, cy0 = w // 4, h // 4
            cx1, cy1 = (w * 3) // 4, (h * 3) // 4
            crop = im.crop((cx0, cy0, cx1, cy1))
            data = crop.tobytes()
            return sum(data) / len(data) if data else 0.0
    except ImportError:
        pass
    return _png_mean_luma_pure(path)


def _png_mean_luma_pure(path: str) -> float | None:
    """Pure-Python PNG luma. Handles RGB/RGBA/grayscale 8-bit, no filter
    reconstruction beyond None/Sub/Up. Good enough for not-black assertion."""
    try:
        import zlib
        import struct
        with open(path, "rb") as f:
            sig = f.read(8)
            if sig != b"\x89PNG\r\n\x1a\n":
                return None
            w = h = bit = color = 0
            idat = bytearray()
            while True:
                hdr = f.read(8)
                if len(hdr) < 8:
                    break
                length, ctype = struct.unpack(">I4s", hdr)
                data = f.read(length)
                f.read(4)  # crc
                if ctype == b"IHDR":
                    w, h, bit, color = struct.unpack(">IIBB", data[:10])
                elif ctype == b"IDAT":
                    idat += data
                elif ctype == b"IEND":
                    break
            if not w or bit != 8 or color not in (0, 2, 6):
                return None
            channels = {0: 1, 2: 3, 6: 4}[color]
            stride = w * channels
            raw = zlib.decompress(bytes(idat))
            prev = bytearray(stride)
            out_sum = 0
            out_count = 0
            cy0, cy1 = h // 4, (h * 3) // 4
            cx0, cx1 = w // 4, (w * 3) // 4
            for y in range(h):
                filt = raw[y * (stride + 1)]
                row = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
                if filt == 1:
                    for i in range(channels, stride):
                        row[i] = (row[i] + row[i - channels]) & 0xFF
                elif filt == 2:
                    for i in range(stride):
                        row[i] = (row[i] + prev[i]) & 0xFF
                elif filt in (3, 4):
                    return None  # unsupported, weak path acceptable
                prev = row
                if y < cy0 or y >= cy1:
                    continue
                for x in range(cx0, cx1):
                    off = x * channels
                    if channels == 1:
                        v = row[off]
                    else:
                        r, g, b = row[off], row[off + 1], row[off + 2]
                        v = (r * 30 + g * 59 + b * 11) // 100
                    out_sum += v
                    out_count += 1
            return out_sum / out_count if out_count else 0.0
    except Exception:
        return None


def assert_not_black(path: str, threshold: float = 16.0) -> tuple[bool, str]:
    lum = png_mean_luma(path)
    if lum is None:
        # Fallback: file-size heuristic.
        try:
            sz = os.path.getsize(path)
            if sz > 32 * 1024:
                return True, f"size={sz} (luma decode unavailable; degraded)"
            return False, f"size={sz} (luma decode unavailable; degraded)"
        except OSError as e:
            return False, str(e)
    return lum >= threshold, f"luma={lum:.1f} threshold={threshold}"


def wait_visible(process_name: str, screenshot_path: str, timeout: float = 30.0,
                 poll_ms: int = 500, luma_threshold: float = 16.0) -> dict:
    """Universal "is the frontend up?" probe. Works on KMS/sway/weston."""
    deadline = time.time() + timeout
    pid_seen_at = None
    visible_at = None

    while time.time() < deadline:
        pids = pgrep(process_name)
        if pids and pid_seen_at is None:
            pid_seen_at = time.time()
        if pids:
            tmp = f"{screenshot_path}.probe"
            if screenshot(tmp):
                ok, _ = assert_not_black(tmp, luma_threshold)
                if ok:
                    os.replace(tmp, screenshot_path)
                    visible_at = time.time()
                    return {
                        "visible": True,
                        "pid": pids[0],
                        "pid_seen_ms": int((pid_seen_at - (deadline - timeout)) * 1000),
                        "first_frame_ms": int((visible_at - pid_seen_at) * 1000)
                            if pid_seen_at else None,
                    }
        time.sleep(poll_ms / 1000.0)

    return {"visible": False, "pid": pids[0] if pids else None, "reason": "timeout"}
