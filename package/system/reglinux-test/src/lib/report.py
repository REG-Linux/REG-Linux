# Writers: report.json, report.junit.xml, report.md, history.csv, env.json.

import csv
import html
import json
import os
from datetime import datetime
from pathlib import Path


def write_reports(run: dict) -> dict:
    rd = Path(run["run_dir"])
    paths = {
        "json": rd / "report.json",
        "junit": rd / "report.junit.xml",
        "md": rd / "report.md",
        "env": rd / "env.json",
        "history": _history_path(rd.parent),
    }
    paths["json"].write_text(json.dumps(run, indent=2, default=str))
    paths["env"].write_text(json.dumps(run["env"], indent=2, default=str))
    paths["junit"].write_text(_junit(run))
    paths["md"].write_text(_markdown(run))
    _append_history(paths["history"], run)
    _refresh_latest_symlink(rd)
    return paths


def _junit(run: dict) -> str:
    s = run["summary"]
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           f'<testsuite name="reglinux-test" tests="{s["total"]}" '
           f'failures="{s["fail"]}" skipped="{s["skip"]}" '
           f'time="{run["duration_s"]}">']
    for c in run["cases"]:
        classname = c.get("scenario", "unnamed")
        name = c["id"].rsplit("/", 1)[-1]
        dur_ms = sum(s.get("duration_ms", 0) for s in c.get("steps", []))
        out.append(f'  <testcase classname="{_x(classname)}" '
                   f'name="{_x(name)}" time="{dur_ms / 1000:.3f}">')
        if c["status"] == "fail":
            err = _x(c.get("error") or "fail")
            log = _x((Path(c["log"]).read_text()[-4000:]) if c.get("log") else "")
            out.append(f'    <failure message="{err}"><![CDATA[{log}]]></failure>')
        elif c["status"] == "skip":
            out.append(f'    <skipped message="{_x(c.get("error") or "skip")}"/>')
        out.append("  </testcase>")
    out.append("</testsuite>")
    return "\n".join(out)


def _markdown(run: dict) -> str:
    s = run["summary"]
    env = run["env"]
    disp = env["display"]
    lines = [
        f"# reglinux-test report — {run['run_id']}",
        "",
        f"- **Board**: {env.get('board', 'unknown')}  ",
        f"- **Arch**: {env.get('arch', '')}  ",
        f"- **Kernel**: {env.get('kernel', '')}  ",
        f"- **Display**: {disp.get('backend')} / {disp.get('compositor', '-')}"
        + (f" ({disp.get('compositor_variant')})"
           if disp.get('compositor_variant') else ""),
        f"- **Xwayland active**: {disp.get('xwayland_active')}",
        f"- **Duration**: {run['duration_s']}s",
        "",
        f"## Summary",
        "",
        f"| pass | fail | skip | total |",
        f"|------|------|------|-------|",
        f"| {s['pass']} | {s['fail']} | {s['skip']} | {s['total']} |",
        "",
        "## Cases",
        "",
        "| status | id | duration | error |",
        "|--------|----|----------|-------|",
    ]
    for c in run["cases"]:
        dur_ms = sum(st.get("duration_ms", 0) for st in c.get("steps", []))
        emoji = {"pass": "✅", "fail": "❌", "skip": "⊝"}.get(c["status"], "?")
        err = (c.get("error") or "").replace("|", "\\|")[:80]
        lines.append(f"| {emoji} | `{c['id']}` | {dur_ms} ms | {err} |")
    if disp.get("degraded_probes"):
        lines += ["", "## Degraded probes",
                  ", ".join(disp["degraded_probes"])]
    return "\n".join(lines) + "\n"


def _history_path(out_root: Path) -> Path:
    return out_root / "history.csv"


def _append_history(path: Path, run: dict):
    new = not path.exists()
    env = run["env"]
    disp = env["display"]
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["run_id", "board", "arch", "backend",
                        "compositor_variant", "scenario", "case_id",
                        "status", "duration_ms", "degraded", "error"])
        for c in run["cases"]:
            dur_ms = sum(s.get("duration_ms", 0) for s in c.get("steps", []))
            degraded = "1" if any(s.get("degraded") for s in c.get("steps", [])) \
                else ""
            w.writerow([run["run_id"], env.get("board", ""), env.get("arch", ""),
                        disp.get("backend", ""),
                        disp.get("compositor_variant", ""),
                        c.get("scenario", ""), c["id"], c["status"], dur_ms,
                        degraded, (c.get("error") or "")[:200]])


def _refresh_latest_symlink(run_dir: Path):
    latest = run_dir.parent / "latest"
    try:
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        os.symlink(run_dir.name, latest)
    except OSError:
        pass


def _x(s: str) -> str:
    return html.escape(s or "", quote=True)
