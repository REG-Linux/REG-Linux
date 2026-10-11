# reglinux-test-wl-probe

Tiny Wayland toplevel enumerator used by the `reglinux-test` Python harness.

Outputs one JSON object per toplevel, then a terminating `{"end":true}`:

```
{"id":"...","app_id":"regstation","title":"REG-Station","activated":true,"maximized":false,"minimized":false,"fullscreen":false}
{"end":true}
```

The four state flags (`activated`, `maximized`, `minimized`, `fullscreen`)
are boolean when the protocol exposes them and `null` otherwise. The
vendored `ext_foreign_toplevel_list_v1` (v1) does not advertise state
events, so against an ext-only compositor those fields are reported as
`null`. `zwlr_foreign_toplevel_manager_v1` does expose all four.

Supports both modern (`ext_foreign_toplevel_list_v1`, sway 1.9+, weston 13+)
and legacy wlroots (`zwlr_foreign_toplevel_manager_v1`) protocols. Falls back
automatically; `--protocol ext|wlr` forces a choice.

## CLI

```
reglinux-test-wl-probe                                       # list once, exit 0
reglinux-test-wl-probe --wait <app_id> --timeout <sec>       # block until present
reglinux-test-wl-probe --wait-activated <app_id> --timeout <sec>  # block until focused
reglinux-test-wl-probe --protocol auto|ext|wlr
reglinux-test-wl-probe --help
```

`--wait-activated` requires a protocol that actually exposes activation
state. If only ext (without state) is advertised and no wlr fallback is
available, the tool prints `{"error":"no_activation_state","tried":["ext","wlr"]}`
and exits 3. When both ext and wlr are advertised under `--protocol auto`,
`--wait-activated` automatically routes through wlr.

Exit codes:

| code | meaning                                                          |
|------|------------------------------------------------------------------|
| 0    | success                                                          |
| 1    | generic error (cannot connect, bad args, protocol read failure)  |
| 2    | `--wait` / `--wait-activated` timed out                          |
| 3    | no foreign-toplevel protocol advertised, OR `--wait-activated`   |
|      | requested but the selected protocol exposes no activation state  |

## Host build

```
sudo apt install libwayland-dev wayland-protocols
make
```

The target build picks up `wayland`, `wayland-protocols`, and `host-wayland`
through the parent buildroot package — no extra wiring needed.

Vendored protocol XMLs live under `protocols/`; they are intentionally pinned
to avoid skew with whatever `wayland-protocols` version the target sysroot
provides.

## License

MIT, matching the upstream wayland-protocols XMLs.
