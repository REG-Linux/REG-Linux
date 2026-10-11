# reglinux-test

System-level test + fuzz harness for REG-Linux. Black-box: spawns existing
CLIs only (`regmsg`, `regstation`, `libra_test`, `/dev/uinput`). No socket
re-implementation, no FFI.

Validates:

- **REG-Station** lifecycle — start / wait visible / inject input / stop
- **regmsgd IPC launcher** — `launcher.launch|status|stop|resolve|generate`
- **libra** in-process libretro runs — headless, deterministic
- **Display matrix** — rotation × resolution, VT switch, HDMI hotplug
- **Fuzzing** — random ROMs, mutated CLI args, lifecycle sequences

Backends auto-detected at runtime: **sway**, **weston**, **wayland (generic)**,
**bare KMS**. Probes degrade gracefully when compositor IPC is absent;
`reglinux-test-wl-probe` (optional) lifts weston from degraded by enumerating
toplevels through `ext_foreign_toplevel_list_v1` / `zwlr_foreign_toplevel_manager_v1`.

## On-device usage

SSH to target. All commands need root or `userdata` group.

### Quick checks

```sh
reglinux-test env                       # JSON: board, arch, display backend, regmsg/regstation versions
reglinux-test list                      # list installed scenarios
reglinux-test --help                    # full CLI
```

### Run scenarios

```sh
# all scenarios (full smoke)
reglinux-test run

# named scenarios only
reglinux-test run ipc_contract frontend_lifecycle

# convenience aliases
reglinux-test frontend                  # = run frontend_lifecycle
reglinux-test ipc                       # = run ipc_contract + launcher_smoke
reglinux-test libra                     # = run core_matrix (libra backend)

# narrow matrix by case-id glob
reglinux-test run core_matrix --filter '*/megadrive/*'

# longer per-game runtime (default 10s)
reglinux-test run launcher_smoke -t 30 -s   # -s = screenshot every step

# only scenarios compatible with current display
reglinux-test run --backend-filter sway     # sway-required scenarios skipped on weston/kms

# CI guard: abort if backend isn't what we expect
reglinux-test run --force-backend weston
```

### Fuzz

```sh
reglinux-test fuzz rom --time 600           # 10min ROM fuzz via libra
reglinux-test fuzz cli --time 120           # mutated regmsg argv
reglinux-test fuzz lifecycle --time 300     # random launch/stop seqs
```

Each fuzz run produces `/userdata/reportTest/fuzz-<target>-<seed>/` with
`fuzz.log` + crash corpus (`hang-*.rom`, `sig-*.rom`).

### Outputs

```
/userdata/reportTest/
├── latest             → symlink to most recent run
├── run-20260513T152345/
│   ├── report.json    machine-readable
│   ├── report.junit.xml  CI/Jenkins/GitHub
│   ├── report.md      human, with screenshots
│   ├── env.json       board+display fingerprint
│   └── cases/
│       └── <case-id>/
│           ├── cmd.log         every subprocess + stdout/stderr
│           ├── *.png           screenshots
│           └── libra/          libra artifacts (frame.ppm + audio.raw)
└── history.csv        rolling, one line per case across runs
```

### Inspect a failure

```sh
# print every cmd that ran for a failed case
reglinux-test replay /userdata/reportTest/latest/cases/launcher_smoke__psx

# tail the markdown report
less /userdata/reportTest/latest/report.md

# query history
awk -F, '$8=="fail" && $4=="weston"' /userdata/reportTest/history.csv
```

### Custom game list (optional, TODO)

Drop a yml in `/userdata/system/configuration/reglinux-test/games.yml`:

```yaml
megadrive: [/userdata/roms/megadrive/sonic.md]
psx: [/userdata/roms/psx/road_rash.PBP]
```

Today's scenarios auto-pick the first matching ROM per system. Deterministic
game-list support is the next thing to wire.

### Typical first-boot sequence

```sh
# 1. sanity: env detection works
reglinux-test env | jq .display

# 2. IPC contract (no display, no ROMs needed)
reglinux-test ipc

# 3. one full lifecycle pass
reglinux-test run frontend_lifecycle -s

# 4. inspect
cat /userdata/reportTest/latest/report.md
```

### Common failure modes + meaning

| Symptom | Likely cause |
|---|---|
| `backend=kms_absent` | no `/dev/dri/card*` — driver not loaded |
| every IPC step → `rc_nonzero` | regmsgd not running. `pgrep regmsgd` |
| `wait_visible` timeout, pid present | wrong output (handheld+dock); check `regmsg screen getoutput` |
| `assert_not_black` fail, pid present | compositor put window on wrong output OR luma threshold needs tuning |
| `no_orphan_emulator` fail | previous run left emu running. `system-es-swissknife --emukill` |
| `wl_probe_missing` | board has no Wayland — expected on bare-KMS targets |

### Quick smoke (one-liner for CI)

```sh
reglinux-test run ipc_contract --keep-going \
    && [ "$(jq .summary.fail /userdata/reportTest/latest/report.json)" = "0" ]
```

Exit 0 = clean. Non-zero = check the report.

## Scenario authoring

Scenarios live in `/usr/share/reglinux-test/scenarios/*.yml`. Each is a small
declarative spec: matrix expansion, step sequence, cleanup block.

Minimal example:

```yaml
id: my_scenario
description: what it tests
requires_display: any            # any | kms | wayland | sway | weston

defaults:
  on_failure: continue           # continue | halt | cleanup (default: halt)

matrix:
  system: [megadrive, snes]

steps:
  - ipc: launcher_launch
    args: ["{system}", "/path/to/rom"]
    capture: launch
    fail_codes: [no_emulator, spawn_failed]
  - sleep: "{time_per_game}"
  - probe: screenshot
    save: "{case_dir}/{system}.png"
  - probe: assert_not_black
    path: "{case_dir}/{system}.png"
  - ipc: launcher_stop
    args: ["{launch.pid}"]

cleanup:
  - frontend: emukill
    allow_fail: true
```

### Step types

| Type | What it does |
|---|---|
| `run: <cmd>` | shell command; `expect_rc`, `expect_json`, `capture`, `fail_codes` |
| `ipc: <method>` | call `regmsg` via Python wrapper; `args`, `capture`, `fail_codes` |
| `probe: <kind>` | `screenshot`, `wait_visible`, `assert_not_black`, `window_exists`, `is_process_alive`, `no_orphan_emulator` |
| `inject: <kind>` | `button` (gamepad) or `key`; uses `/dev/uinput` |
| `frontend: <action>` | `start`, `stop`, `restart`, `emukill` |
| `libra:` | run libra_test against a core+rom |
| `sleep: N` | seconds |
| `assert: "{x} == y"` | trivial comparison |

### Step modifiers

| Field | Effect |
|---|---|
| `allow_fail: true` | step may fail without aborting the case |
| `severity: warn` | non-fatal; logged, doesn't change case status |
| `on_failure: continue\|halt\|cleanup` | per-step override of failure policy |
| `only_if_backend: [sway]` | skipped when current backend differs |
| `fallback: <probe>` | when gated out, replace with this probe |
| `timeout: N` | seconds (default 30) |

### Variable interpolation

`{var}` expands from context. Dotted access for captured JSON: `{launch.pid}`.

Built-ins available in every step:
- `{run_dir}`, `{case_dir}`
- `{backend}` — current display backend
- `{time_per_game}`
- everything declared under `defaults:`
- everything bound by `matrix:`
- everything captured by previous steps

## Architecture

```
src/
├── reglinux-test                 entry, argparse
├── lib/
│   ├── engine.py                 scenario interpreter, matrix expansion
│   ├── runner.py                 subprocess wrapper, timeout, log capture
│   ├── ipc.py                    regmsg CLI wrapper, JSON parsing
│   ├── frontend.py               regstation lifecycle via init.d + swissknife
│   ├── libra.py                  libra_test wrapper, audio RMS, frame check
│   ├── probe.py                  screenshot, luma, pgrep, /proc parsing
│   ├── uinput.py                 /dev/uinput button/key injection
│   ├── env.py                    board, arch, display fingerprint
│   ├── known_emulators.py        parses rs_systems.cfg, 200+ systems
│   ├── report.py                 JSON / JUnit / Markdown / CSV writers
│   ├── fuzz.py                   black-box fuzzers
│   └── display/
│       ├── base.py               abstract Backend
│       ├── kms.py                bare DRM
│       ├── sway.py               rich IPC, subscribe-based wait_window_event
│       ├── weston.py             degraded, lifted by wl-probe
│       ├── wayland_generic.py    unknown compositor fallback
│       └── _wl_probe.py          shells out to reglinux-test-wl-probe
├── scenarios/*.yml               declarative test specs
└── wl-probe/                     optional C helper (Wayland-only)
    ├── main.c                    foreign-toplevel enumerator
    ├── Makefile
    └── protocols/                vendored XML
```

## Build / install

Buildroot package: `BR2_PACKAGE_REGLINUX_TEST=y`.

Sub-options:
- `BR2_PACKAGE_REGLINUX_TEST_WL_PROBE` (default `y` if `BR2_PACKAGE_WAYLAND`) —
  builds and installs the optional Wayland helper. Disable on bare-KMS
  boards (a133, cha, de10nano, jz4770, mini) to skip the wayland-protocols
  + host-wayland-scanner build chain.

Dependencies:
- `python3`, `python-pyyaml`, `python-pillow`
- (optional) `wayland`, `wayland-protocols`, `host-wayland` — only when wl-probe enabled

Install locations:
- `/usr/bin/reglinux-test`
- `/usr/bin/reglinux-test-wl-probe` (if wl-probe enabled)
- `/usr/lib/reglinux-test/lib/`
- `/usr/share/reglinux-test/scenarios/`

## Limits

- `ext_foreign_toplevel_list_v1` v1 has no state event → `assert_focused`
  returns `null` on ext-only compositors (weston 13 today). sway exposes both
  ext + wlr → works.
- `move_to_output` cannot be probed on weston — no IPC equivalent. KMS/sway only.
- Single-slot launcher: concurrent emulator runs unsupported (regmsgd limitation).
- Scenario YAML can interpolate `{var}` and dotted JSON paths, but no arithmetic
  or conditionals. Move logic into Python helpers if needed.

## License

GPL-3.0. The `wl-probe` C helper is MIT (matches wayland-protocols).
