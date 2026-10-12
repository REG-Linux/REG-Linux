# regmsg IPC wrapper. No socket — spawns the regmsg CLI and parses output.

import json
from typing import Any

from .runner import run, CmdResult


class IpcError(Exception):
    def __init__(self, code: str, message: str, raw: str = ""):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.raw = raw


def regmsg(*args: str, timeout: float = 30.0) -> CmdResult:
    return run(["regmsg", *args], timeout=timeout)


def regmsg_json(*args: str, timeout: float = 30.0) -> Any:
    r = regmsg(*args, timeout=timeout)
    if not r.ok():
        _raise_from(r)
    text = r.stdout.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise IpcError("invalid_json", str(e), text) from e


def launcher_resolve(system: str) -> dict:
    return regmsg_json("launcher", "resolve", system)


def launcher_generate(system: str, rom: str, options: dict | None = None) -> dict:
    args = ["launcher", "generate", system, rom]
    if options is not None:
        args.append(json.dumps(options))
    return regmsg_json(*args)


def launcher_launch(system: str, rom: str, options: dict | None = None) -> dict:
    args = ["launcher", "launch", system, rom]
    if options is not None:
        args.append(json.dumps(options))
    return regmsg_json(*args, timeout=60.0)


def launcher_status(pid: int) -> dict:
    return regmsg_json("launcher", "status", str(pid))


def launcher_stop(pid: int) -> dict:
    return regmsg_json("launcher", "stop", str(pid), timeout=15.0)


def launcher_reload() -> dict:
    return regmsg_json("launcher", "reload")


# Daemon default (config.rs DEFAULT_SYSTEM_CONF_PATH).
SYSTEM_CONF = "/userdata/system/system.conf"


def systemconf_get(key: str) -> str:
    # getconfigkey takes keys only — daemon reads its loaded config.
    r = regmsg("systemconf", "getconfigkey", key)
    return r.stdout.strip() if r.ok() else ""


def systemconf_set(key: str, value: str, file: str = SYSTEM_CONF) -> CmdResult:
    # setconfigkey requires the target file first, then key/value pairs.
    return regmsg("systemconf", "setconfigkey", file, key, value)


def screen_listoutputs() -> list[str]:
    r = regmsg("screen", "listoutputs")
    if not r.ok():
        return []
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


def screen_getoutput() -> str:
    r = regmsg("screen", "getoutput")
    return r.stdout.strip() if r.ok() else ""


def screen_listmodes(output: str | None = None) -> list[str]:
    args = ["screen", "listmodes"]
    if output:
        args += ["--output", output]
    r = regmsg(*args)
    if not r.ok():
        return []
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


def screen_setmode(mode: str, output: str | None = None) -> CmdResult:
    args = ["screen", "setmode", mode]
    if output:
        args += ["--output", output]
    return regmsg(*args)


def screen_getrotation(output: str | None = None) -> str:
    args = ["screen", "getrotation"]
    if output:
        args += ["--output", output]
    r = regmsg(*args)
    return r.stdout.strip() if r.ok() else ""


def screen_screenshot(output: str | None = None) -> CmdResult:
    # `screen getscreenshot` takes no path — the daemon writes a
    # timestamped file under /userdata/screenshots. Optional -o output.
    args = ["screen", "getscreenshot"]
    if output:
        args += ["-o", output]
    return regmsg(*args, timeout=10.0)


def _raise_from(r: CmdResult):
    txt = r.stderr.strip() or r.stdout.strip()
    # Daemon error shape: "ERR {...}"
    if txt.startswith("ERR "):
        try:
            blob = json.loads(txt[4:])
            raise IpcError(blob.get("code", "unknown"),
                           blob.get("message", ""), raw=txt)
        except json.JSONDecodeError:
            pass
    raise IpcError("rc_nonzero", f"rc={r.rc} stderr={txt[:200]}", raw=txt)
