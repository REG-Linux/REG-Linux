# Black-box fuzzers. Subprocess-only — feeds garbage to real binaries.

import json
import os
import random
import shutil
import string
import time
from pathlib import Path

from . import ipc, libra
from .runner import run as _sh


def run(args):
    target = args.target
    seed = args.seed or int(time.time())
    rng = random.Random(seed)
    out_dir = Path(args.out) / f"fuzz-{target}-{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    log = (out_dir / "fuzz.log").open("w")
    log.write(f"# fuzz target={target} seed={seed} duration={args.time}s\n\n")

    if target == "rom":
        report = _fuzz_rom(rng, args.time, out_dir, log)
    elif target == "cli":
        report = _fuzz_cli(rng, args.time, out_dir, log)
    elif target == "lifecycle":
        report = _fuzz_lifecycle(rng, args.time, out_dir, log)
    else:
        log.write(f"unknown target: {target}\n")
        log.close()
        return 2

    (out_dir / "fuzz_report.json").write_text(json.dumps(report, indent=2))
    log.close()
    print(f"\nReport: {out_dir}")
    return 0 if not report["crashes"] else 1


def _fuzz_rom(rng, duration, out_dir, log):
    deadline = time.time() + duration
    crashes = []
    runs = 0
    # Mutate any small file we can find; default to /dev/urandom blobs.
    while time.time() < deadline:
        rom_path = out_dir / "input.rom"
        size = rng.randint(64, 64 * 1024)
        rom_path.write_bytes(os.urandom(size))
        # Pick a libretro core if present.
        cores = list(Path("/usr/lib/libretro").glob("*_libretro.so")) \
            if Path("/usr/lib/libretro").exists() else []
        if not cores:
            log.write("no libretro cores found, abort\n")
            break
        core = rng.choice(cores)
        res = libra.run_core(str(core), str(rom_path), frames=60,
                             out_dir=str(out_dir / "lr"), timeout=10.0)
        runs += 1
        if not res["ok"] and res.get("timed_out"):
            crashes.append({"kind": "hang", "core": core.name,
                            "size": size, "rc": res["rc"]})
            shutil.copy(rom_path, out_dir / f"hang-{runs}.rom")
        elif res["rc"] < 0:
            crashes.append({"kind": "signal", "core": core.name,
                            "size": size, "rc": res["rc"]})
            shutil.copy(rom_path, out_dir / f"sig-{runs}.rom")
        log.write(f"#{runs} core={core.name} size={size} rc={res['rc']} "
                  f"timed_out={res.get('timed_out')}\n")
    return {"runs": runs, "crashes": crashes, "duration_s": duration}


def _fuzz_cli(rng, duration, out_dir, log):
    deadline = time.time() + duration
    runs = 0
    crashes = []
    daemon_dropped = False
    while time.time() < deadline:
        cmd = ["regmsg", "launcher", "launch",
               _rand_str(rng, 20), _rand_str(rng, 40),
               _rand_json(rng)]
        r = _sh(cmd, timeout=5)
        runs += 1
        log.write(f"#{runs} rc={r.rc} stderr={r.stderr.strip()[:120]}\n")
        # Daemon should still be up afterwards.
        ping = _sh(["pgrep", "-x", "regmsgd"], timeout=3)
        if not ping.ok():
            daemon_dropped = True
            crashes.append({"kind": "daemon_dropped_after",
                            "cmd": cmd, "rc": r.rc})
            break
    return {"runs": runs, "crashes": crashes, "duration_s": duration,
            "daemon_dropped": daemon_dropped}


def _fuzz_lifecycle(rng, duration, out_dir, log):
    deadline = time.time() + duration
    actions = ["launch", "stop", "status", "sleep"]
    last_pid = None
    runs = 0
    crashes = []
    while time.time() < deadline:
        a = rng.choice(actions)
        try:
            if a == "launch":
                # Use generic system, no real ROM, expect spawn_failed or busy
                res = ipc.launcher_launch("megadrive", "/tmp/none.bin")
                last_pid = res.get("pid")
            elif a == "stop" and last_pid:
                ipc.launcher_stop(last_pid)
                last_pid = None
            elif a == "status" and last_pid:
                ipc.launcher_status(last_pid)
            else:
                time.sleep(rng.random())
        except ipc.IpcError as e:
            log.write(f"#{runs} {a} → {e.code}: {e.message}\n")
            if e.code in ("invalid_json", "rc_nonzero"):
                # rc_nonzero with stderr noise is expected; only flag
                # if regmsgd died.
                ping = _sh(["pgrep", "-x", "regmsgd"], timeout=3)
                if not ping.ok():
                    crashes.append({"kind": "daemon_dropped", "action": a,
                                     "error": str(e)})
                    break
        runs += 1
    return {"runs": runs, "crashes": crashes, "duration_s": duration}


def _rand_str(rng, n):
    alpha = string.ascii_letters + string.digits + "/.-_"
    return "".join(rng.choice(alpha) for _ in range(n))


def _rand_json(rng):
    keys = ["core", "ratio", "shader", "rewind", "smooth", "bezel"]
    obj = {rng.choice(keys): _rand_str(rng, 8) for _ in range(rng.randint(0, 5))}
    return json.dumps(obj)
