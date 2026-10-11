# Subprocess wrapper. Captures stdout/stderr, enforces timeout.

import os
import shlex
import signal
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass
class CmdResult:
    argv: Sequence[str]
    rc: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False
    started_at: float = field(default_factory=time.time)

    def ok(self) -> bool:
        return self.rc == 0 and not self.timed_out

    def render_log(self) -> str:
        cmd = " ".join(shlex.quote(a) for a in self.argv)
        head = f"$ {cmd}\n[rc={self.rc} dur={self.duration_ms}ms"
        if self.timed_out:
            head += " TIMEOUT"
        head += "]\n"
        body = ""
        if self.stdout:
            body += f"--- stdout ---\n{self.stdout}\n"
        if self.stderr:
            body += f"--- stderr ---\n{self.stderr}\n"
        return head + body


def run(argv, *, timeout: float = 30.0, env: Optional[dict] = None,
        input_bytes: Optional[bytes] = None, cwd: Optional[str] = None) -> CmdResult:
    started = time.time()
    real_env = os.environ.copy()
    if env:
        real_env.update(env)

    try:
        proc = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=real_env,
            cwd=cwd,
            preexec_fn=os.setsid,
        )
    except (FileNotFoundError, PermissionError) as e:
        dur = int((time.time() - started) * 1000)
        return CmdResult(argv=list(argv), rc=127, stdout="",
                         stderr=str(e), duration_ms=dur)

    timed_out = False
    try:
        out, err = proc.communicate(input=input_bytes, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            out, err = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            out, err = proc.communicate()

    dur = int((time.time() - started) * 1000)
    return CmdResult(
        argv=list(argv),
        rc=proc.returncode if proc.returncode is not None else -1,
        stdout=out.decode("utf-8", "replace") if out else "",
        stderr=err.decode("utf-8", "replace") if err else "",
        duration_ms=dur,
        timed_out=timed_out,
        started_at=started,
    )


def run_shell(cmd: str, **kw) -> CmdResult:
    return run(["sh", "-c", cmd], **kw)
