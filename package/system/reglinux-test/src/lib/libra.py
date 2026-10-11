# libra in-process runner. Spawns libra_test binary (already in libra/test/).

import os
import shutil
import struct
from pathlib import Path

from .runner import run


def find_core(core_name: str, libretro_dir: str = "/usr/lib/libretro") -> str | None:
    cands = [
        f"{libretro_dir}/{core_name}_libretro.so",
        f"{libretro_dir}/{core_name}.so",
    ]
    for c in cands:
        if Path(c).exists():
            return c
    return None


def run_core(core_path: str, rom: str, frames: int = 600,
             out_dir: str = "/tmp/libra-run", timeout: float = 60.0) -> dict:
    binary = shutil.which("libra_test")
    if not binary:
        return {"ok": False, "error": "libra_test binary not on PATH"}

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    frame_ppm = out / "frame.ppm"
    audio_raw = out / "audio.raw"

    r = run([binary, core_path, rom, str(frames)],
            timeout=timeout, cwd=str(out))

    metrics = {
        "frame_present": frame_ppm.exists() and frame_ppm.stat().st_size > 0,
        "audio_present": audio_raw.exists() and audio_raw.stat().st_size > 0,
    }
    if metrics["audio_present"]:
        metrics["audio_rms"] = audio_rms(str(audio_raw))
    if metrics["frame_present"]:
        metrics["frame_size_bytes"] = audio_raw.stat().st_size

    return {
        "ok": r.ok() and metrics["frame_present"],
        "rc": r.rc,
        "timed_out": r.timed_out,
        "duration_ms": r.duration_ms,
        "stdout_tail": r.stdout[-2000:],
        "stderr_tail": r.stderr[-2000:],
        "metrics": metrics,
    }


def audio_rms(path: str, max_frames: int = 48000 * 4) -> float | None:
    """RMS of int16 stereo PCM. Returns None on read error."""
    try:
        with open(path, "rb") as f:
            data = f.read(max_frames * 4)
        n = len(data) // 2
        if n == 0:
            return 0.0
        samples = struct.unpack(f"<{n}h", data[:n * 2])
        sq = sum(s * s for s in samples)
        return (sq / n) ** 0.5
    except OSError:
        return None
