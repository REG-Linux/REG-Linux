# Scenario engine. YAML → cases → step interpreter.

import fnmatch
import itertools
import json
import os
import random
import re
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import yaml

from . import frontend, ipc, libra, probe, uinput
from .runner import run

VAR_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_.]*)\}")


class Engine:
    def __init__(self, *, env: dict, out_root: str, time_per_game: int = 10,
                 screenshot: bool = False, keep_going: bool = False,
                 backend_filter: str | None = None,
                 case_filter: str | None = None, seed: int = 0):
        self.env = env
        self.time_per_game = time_per_game
        self.screenshot = screenshot
        self.keep_going = keep_going
        self.backend_filter = backend_filter
        self.case_filter = case_filter
        self.seed = seed
        self.rng = random.Random(seed)
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.run_dir = Path(out_root) / f"run-{ts}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.backend = self.env["display"]["backend"]

    # ---- entry points ----

    def run_all(self, scenarios) -> dict:
        cases = []
        started = time.time()
        for path in scenarios:
            try:
                spec = yaml.safe_load(Path(path).read_text())
            except (OSError, yaml.YAMLError) as e:
                cases.append(self._error_case(str(path), f"yaml: {e}"))
                continue
            if not isinstance(spec, dict):
                cases.append(self._error_case(str(path), "scenario not a mapping"))
                continue

            req = spec.get("requires_display", "any")
            if not self._backend_compatible(req):
                cases.append(self._skip_case(spec.get("id", Path(path).stem),
                                            f"requires_display={req}"))
                continue
            if self.backend_filter and self.backend_filter != "any" \
                    and self.backend != self.backend_filter:
                cases.append(self._skip_case(spec.get("id", Path(path).stem),
                                             f"backend-filter={self.backend_filter}"))
                continue

            for case in self._expand_matrix(spec):
                if self.case_filter and not fnmatch.fnmatch(case["id"],
                                                            self.case_filter):
                    continue
                result = self._run_case(spec, case)
                cases.append(result)
                if result["status"] == "fail" and not self.keep_going:
                    # finish current scenario only
                    pass

        duration_s = round(time.time() - started, 2)
        run = {
            "run_id": self.run_dir.name,
            "started_at": datetime.now().isoformat(),
            "duration_s": duration_s,
            "env": self.env,
            "summary": _summarise(cases),
            "cases": cases,
            "run_dir": str(self.run_dir),
        }
        return run

    # ---- scenario / case expansion ----

    def _expand_matrix(self, spec: dict) -> list[dict]:
        base_id = spec.get("id", "unnamed")
        matrix = spec.get("matrix", {}) or {}
        systems = spec.get("systems")
        if systems:
            matrix.setdefault("system", systems)
        if not matrix:
            return [{"id": base_id, "vars": {}}]

        keys = list(matrix.keys())
        product = list(itertools.product(*(matrix[k] for k in keys)))
        if self.seed:
            self.rng.shuffle(product)

        out = []
        for combo in product:
            vars_ = dict(zip(keys, combo))
            cid = base_id + "/" + "_".join(str(v) for v in combo)
            out.append({"id": cid, "vars": vars_})
        return out

    def _backend_compatible(self, req: str) -> bool:
        if req in ("any", None):
            return True
        if req == self.backend:
            return True
        if req == "wayland" and self.backend in ("sway", "weston",
                                                  "wayland_generic"):
            return True
        if req == "compositor" and self.backend in ("sway", "weston",
                                                     "wayland_generic"):
            return True
        return False

    # ---- per-case execution ----

    def _run_case(self, spec: dict, case: dict) -> dict:
        cid = case["id"]
        case_dir = self.run_dir / "cases" / cid.replace("/", "__")
        case_dir.mkdir(parents=True, exist_ok=True)
        log_path = case_dir / "cmd.log"

        ctx: dict[str, Any] = {
            "run_dir": str(self.run_dir),
            "case_dir": str(case_dir),
            "time_per_game": self.time_per_game,
            "backend": self.backend,
            "screenshot": self.screenshot,
            **case["vars"],
        }
        # Defaults from scenario `defaults:` block.
        for k, v in (spec.get("defaults") or {}).items():
            ctx.setdefault(k, v)

        steps = spec.get("steps", [])
        step_results = []
        status = "pass"
        error = None
        scenario_default_on_failure = (
            (spec.get("defaults") or {}).get("on_failure", "halt")
        )

        with open(log_path, "w") as log:
            log.write(f"# case={cid}\n# vars={json.dumps(case['vars'])}\n\n")
            jump_to_cleanup = False
            for idx, step in enumerate(steps):
                if jump_to_cleanup:
                    break
                try:
                    res = self._run_step(step, ctx, log)
                except Exception as e:  # noqa: BLE001
                    res = {"type": "exception", "ok": False, "error": str(e),
                           "trace": traceback.format_exc()}
                step_results.append(res)

                if res.get("ok", False) or res.get("skipped", False):
                    continue

                # legacy allow_fail = on_failure: continue (severity: warn)
                if step.get("allow_fail"):
                    res["severity"] = "warn"
                    continue

                severity = step.get("severity", "error")
                on_fail = step.get("on_failure", scenario_default_on_failure)

                if severity == "warn":
                    res["severity"] = "warn"
                    log.write(f"# WARN step #{idx}: {res.get('error') or res.get('type')}\n")
                    continue

                # severity=error
                if status != "fail":
                    status = "fail"
                    error = res.get("error") or res.get("type")

                if on_fail == "continue" or self.keep_going:
                    log.write(f"# CONTINUE after step #{idx} fail\n")
                    continue
                if on_fail == "cleanup":
                    log.write(f"# JUMP_TO_CLEANUP after step #{idx}\n")
                    jump_to_cleanup = True
                    break
                # default: halt
                break

            # cleanup block: always runs
            for step in spec.get("cleanup", []) or []:
                try:
                    res = self._run_step(step, ctx, log)
                    res["cleanup"] = True
                    step_results.append(res)
                except Exception as e:  # noqa: BLE001
                    step_results.append({"type": "cleanup_exception", "ok": False,
                                          "error": str(e), "cleanup": True})

        return {
            "id": cid,
            "scenario": spec.get("id", "unnamed"),
            "status": status if any(not r.get("skipped") for r in step_results)
                      else "skip",
            "vars": case["vars"],
            "steps": step_results,
            "error": error,
            "log": str(log_path),
            "case_dir": str(case_dir),
        }

    # ---- step interpreter ----

    def _run_step(self, step: dict, ctx: dict, log) -> dict:
        # gating
        only = step.get("only_if_backend")
        if only and self.backend not in only:
            fb = step.get("fallback")
            if not fb:
                return {"type": step_type(step), "skipped": True, "ok": True,
                        "reason": f"backend={self.backend} not in {only}"}
            step = {**step, "probe": fb, "only_if_backend": None,
                    "fallback": None, "degraded": True}

        t = step_type(step)
        handler = _HANDLERS.get(t)
        if not handler:
            return {"type": t, "ok": False, "error": f"unknown step: {t}"}
        return handler(self, step, ctx, log)

    # ---- helpers used by handlers ----

    def _interp(self, value, ctx) -> Any:
        if isinstance(value, str):
            return VAR_RE.sub(lambda m: str(_dig(ctx, m.group(1))), value)
        if isinstance(value, list):
            return [self._interp(v, ctx) for v in value]
        if isinstance(value, dict):
            return {k: self._interp(v, ctx) for k, v in value.items()}
        return value

    def _error_case(self, name: str, msg: str) -> dict:
        return {"id": name, "scenario": name, "status": "fail",
                "vars": {}, "steps": [], "error": msg, "log": ""}

    def _skip_case(self, name: str, msg: str) -> dict:
        return {"id": name, "scenario": name, "status": "skip",
                "vars": {}, "steps": [], "error": msg, "log": ""}


def step_type(step: dict) -> str:
    for k in ("run", "sleep", "probe", "inject", "assert", "launch_via",
              "stop_via", "frontend", "libra", "ipc"):
        if k in step:
            return k
    return "unknown"


def _dig(ctx, dotted: str):
    cur = ctx
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part, "")
        else:
            return ""
    return cur


# -------------------- step handlers --------------------

def _h_run(eng: Engine, step: dict, ctx: dict, log) -> dict:
    cmd = eng._interp(step["run"], ctx)
    if isinstance(cmd, str):
        argv = ["sh", "-c", cmd]
    else:
        argv = [str(x) for x in cmd]
    r = run(argv, timeout=step.get("timeout", 30))
    log.write(r.render_log() + "\n")

    exp_rc = step.get("expect_rc", 0)
    ok = r.rc == exp_rc and not r.timed_out

    out = {"type": "run", "argv": argv, "rc": r.rc, "duration_ms": r.duration_ms,
           "timed_out": r.timed_out, "ok": ok}

    # JSON capture & expectations
    if step.get("capture") or step.get("expect_json") \
            or step.get("expect_json_keys") or step.get("fail_codes"):
        parsed, perr = _try_json(r.stdout)
        if parsed is None and (step.get("expect_json")
                               or step.get("expect_json_keys")):
            ok = False
            out["error"] = f"json parse failed: {perr}"
        else:
            if step.get("capture"):
                ctx[step["capture"]] = parsed if parsed is not None \
                    else r.stdout.strip()
                out["captured"] = ctx[step["capture"]]
            if step.get("expect_json"):
                for k, v in eng._interp(step["expect_json"], ctx).items():
                    if not parsed or parsed.get(k) != v:
                        ok = False
                        out["error"] = f"expect_json {k}={v} got {parsed}"
                        break
            if step.get("expect_json_keys"):
                missing = [k for k in step["expect_json_keys"]
                           if not parsed or k not in parsed]
                if missing:
                    ok = False
                    out["error"] = f"missing json keys: {missing}"
            if step.get("fail_codes") and not r.ok():
                err_json, _ = _try_json(r.stderr or r.stdout)
                code = (err_json or {}).get("code", "")
                if code in step["fail_codes"]:
                    ok = True  # expected fail
                    out["expected_fail"] = code
    out["ok"] = ok
    return out


def _try_json(text: str):
    text = text.strip()
    if not text:
        return None, "empty"
    if text.startswith("ERR "):
        text = text[4:]
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e)


def _h_sleep(eng: Engine, step: dict, ctx: dict, log) -> dict:
    sec = step["sleep"]
    if isinstance(sec, str):
        sec = eng._interp(sec, ctx)
    sec = float(sec)
    log.write(f"# sleep {sec}\n")
    time.sleep(sec)
    return {"type": "sleep", "ok": True, "duration_ms": int(sec * 1000)}


def _h_probe(eng: Engine, step: dict, ctx: dict, log) -> dict:
    kind = step["probe"]
    backend = ctx.get("_backend_obj") or _ensure_backend(ctx)
    target = eng._interp(step.get("target", ""), ctx)

    if kind == "screenshot":
        path = eng._interp(step.get("save", f"{ctx['case_dir']}/shot.png"), ctx)
        ok = backend.screenshot(path)
        log.write(f"# probe screenshot {path} ok={ok}\n")
        return {"type": "probe", "kind": kind, "ok": ok, "path": path}

    if kind == "wait_visible":
        path = eng._interp(step.get("save", f"{ctx['case_dir']}/visible.png"), ctx)
        timeout = float(step.get("timeout", 30))
        res = backend.wait_visible(target or "regstation", path, timeout=timeout)
        log.write(f"# probe wait_visible {target} → {res}\n")
        return {"type": "probe", "kind": kind, "ok": bool(res.get("visible")),
                "info": res}

    if kind == "assert_not_black":
        path = eng._interp(step.get("path", f"{ctx['case_dir']}/visible.png"), ctx)
        ok, info = probe.assert_not_black(path, step.get("threshold", 16.0))
        log.write(f"# probe assert_not_black {path} → {ok} ({info})\n")
        return {"type": "probe", "kind": kind, "ok": ok, "info": info}

    if kind == "window_exists":
        ok, info = backend.window_exists(target)
        if ok is None:
            return {"type": "probe", "kind": kind, "ok": False,
                    "skipped": True, "degraded": True, "info": info}
        log.write(f"# probe window_exists {target} → {ok}\n")
        return {"type": "probe", "kind": kind, "ok": ok, "target": target}

    if kind == "is_process_alive":
        ok = backend.is_process_alive(target)
        log.write(f"# probe is_process_alive {target} → {ok}\n")
        return {"type": "probe", "kind": kind, "ok": ok, "target": target}

    if kind == "no_orphan_emulator":
        from . import known_emulators
        if step.get("patterns"):
            patterns = step["patterns"]
            source = "scenario"
        elif step.get("system"):
            patterns = known_emulators.binaries_for(eng._interp(step["system"], ctx))
            source = f"system={step['system']}"
        else:
            patterns = known_emulators.all_binaries(for_orphan_probe=True)
            source = "all_known"
        found = probe.kill_orphans(patterns)
        ok = not found
        log.write(f"# probe no_orphan_emulator source={source} "
                  f"patterns={len(patterns)} found={list(found.keys())}\n")
        return {"type": "probe", "kind": kind, "ok": ok, "orphans": found,
                "pattern_count": len(patterns), "source": source}

    return {"type": "probe", "kind": kind, "ok": False,
            "error": "unknown probe"}


def _ensure_backend(ctx):
    from .display import detect
    b = detect()
    ctx["_backend_obj"] = b
    return b


def _h_inject(eng: Engine, step: dict, ctx: dict, log) -> dict:
    kind = step["inject"]
    if kind == "button":
        name = eng._interp(step["button"], ctx)
        hold = int(step.get("holdms", 60))
        try:
            uinput.press(name, hold)
            log.write(f"# inject button={name} hold={hold}ms\n")
            return {"type": "inject", "kind": "button", "ok": True}
        except Exception as e:  # noqa: BLE001
            log.write(f"# inject failed: {e}\n")
            return {"type": "inject", "kind": "button", "ok": False, "error": str(e)}
    if kind == "key":
        name = eng._interp(step["key"], ctx)
        hold = int(step.get("holdms", 60))
        try:
            uinput.press(name, hold)
            return {"type": "inject", "kind": "key", "ok": True}
        except Exception as e:  # noqa: BLE001
            return {"type": "inject", "kind": "key", "ok": False, "error": str(e)}
    return {"type": "inject", "ok": False, "error": f"unknown inject: {kind}"}


def _h_assert(eng: Engine, step: dict, ctx: dict, log) -> dict:
    expr = step["assert"]
    val = eng._interp(expr, ctx)
    # Trivial supported forms only:
    #  - "no_orphan_emulator" → delegate to probe
    #  - "{var} == something"
    #  - "{var} != ''"
    if val == "no_orphan_emulator":
        return _h_probe(eng, {"probe": "no_orphan_emulator"}, ctx, log)
    if "==" in val:
        lhs, rhs = (x.strip() for x in val.split("==", 1))
        ok = lhs == rhs
        return {"type": "assert", "ok": ok, "expr": val}
    if "!=" in val:
        lhs, rhs = (x.strip() for x in val.split("!=", 1))
        ok = lhs != rhs
        return {"type": "assert", "ok": ok, "expr": val}
    return {"type": "assert", "ok": False, "error": f"cannot evaluate: {val}"}


def _h_frontend(eng: Engine, step: dict, ctx: dict, log) -> dict:
    action = step["frontend"]
    fn = {"start": frontend.start, "stop": frontend.stop,
          "restart": frontend.restart, "emukill": frontend.emukill}.get(action)
    if not fn:
        return {"type": "frontend", "ok": False,
                "error": f"unknown frontend action: {action}"}
    r = fn()
    log.write(f"# frontend.{action} → {r}\n")
    return {"type": "frontend", "action": action, "ok": r["ok"], "info": r}


def _h_libra(eng: Engine, step: dict, ctx: dict, log) -> dict:
    core = eng._interp(step.get("core", ""), ctx)
    rom = eng._interp(step.get("rom", ""), ctx)
    frames = int(step.get("frames", 600))
    if not core.startswith("/"):
        core = libra.find_core(core) or core
    res = libra.run_core(core, rom, frames=frames,
                         out_dir=f"{ctx['case_dir']}/libra")
    log.write(f"# libra {core} {rom} frames={frames} → ok={res['ok']}\n")
    return {"type": "libra", "ok": res["ok"], "info": res}


def _h_ipc(eng: Engine, step: dict, ctx: dict, log) -> dict:
    method = step["ipc"]
    args = eng._interp(step.get("args", []), ctx)
    try:
        fn = getattr(ipc, method)
        res = fn(*args)
        log.write(f"# ipc {method}({args}) → {json.dumps(res, default=str)[:300]}\n")
        if step.get("capture"):
            ctx[step["capture"]] = res
        return {"type": "ipc", "method": method, "ok": True, "result": res}
    except ipc.IpcError as e:
        log.write(f"# ipc {method} ERR {e.code}: {e.message}\n")
        fail_codes = step.get("fail_codes") or []
        return {"type": "ipc", "method": method,
                "ok": e.code in fail_codes,
                "expected_fail": e.code if e.code in fail_codes else None,
                "error": str(e)}
    except AttributeError:
        return {"type": "ipc", "ok": False,
                "error": f"unknown ipc method: {method}"}


def _h_launch_via(eng: Engine, step: dict, ctx: dict, log) -> dict:
    cmd = eng._interp(step["launch_via"], ctx)
    r = run(["sh", "-c", cmd], timeout=step.get("timeout", 20))
    log.write(r.render_log())
    return {"type": "launch_via", "ok": r.ok(), "rc": r.rc}


def _h_stop_via(eng: Engine, step: dict, ctx: dict, log) -> dict:
    cmd = eng._interp(step["stop_via"], ctx)
    r = run(["sh", "-c", cmd], timeout=step.get("timeout", 20))
    log.write(r.render_log())
    return {"type": "stop_via", "ok": r.ok(), "rc": r.rc}


_HANDLERS = {
    "run": _h_run, "sleep": _h_sleep, "probe": _h_probe,
    "inject": _h_inject, "assert": _h_assert,
    "frontend": _h_frontend, "libra": _h_libra, "ipc": _h_ipc,
    "launch_via": _h_launch_via, "stop_via": _h_stop_via,
}


# -------------------- summary --------------------

def _summarise(cases: list[dict]) -> dict:
    counts = {"pass": 0, "fail": 0, "skip": 0}
    for c in cases:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    counts["total"] = len(cases)
    return counts
