# REG-Station lifecycle: start, wait visible, stop, post-conditions.

from .runner import run


def start() -> dict:
    # init.d hook is the user-facing entrypoint.
    r = run(["/etc/init.d/S31regstation", "start"], timeout=15)
    return _result(r)


def stop() -> dict:
    r = run(["/etc/init.d/S31regstation", "stop"], timeout=20)
    return _result(r)


def restart() -> dict:
    r = run(["system-es-swissknife", "--restart"], timeout=20)
    return _result(r)


def emukill() -> dict:
    r = run(["system-es-swissknife", "--emukill"], timeout=10)
    return _result(r)


def espid_alive() -> bool:
    r = run(["system-es-swissknife", "--espid"], timeout=5)
    # exit 0 means ES alive in current swissknife implementation.
    return r.ok() and "not running" not in r.stdout.lower()


def emu_pid() -> int | None:
    r = run(["system-es-swissknife", "--emupid"], timeout=5)
    if not r.ok():
        return None
    txt = r.stdout.strip()
    for tok in txt.split():
        if tok.isdigit():
            return int(tok)
    return None


def _result(r) -> dict:
    return {"ok": r.ok(), "rc": r.rc, "stdout": r.stdout, "stderr": r.stderr,
            "duration_ms": r.duration_ms}
