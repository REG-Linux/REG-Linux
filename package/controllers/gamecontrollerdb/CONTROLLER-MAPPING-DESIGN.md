# Controller Mapping Design — keep HIDAPI on for SDL2 *and* SDL3

Status: hardware-validated design, **partially implemented** (see §6 for
status; new path gated behind `REGMSG_KEEP_HIDAPI`). Spans three components:
`package/controllers/gamecontrollerdb` (this repo), `REG-Station`
(wizard), and `regmsg` (`regmsgd` launcher).

## 1. Goal

Stop forcing `SDL_JOYSTICK_HIDAPI=0` for SDL2 emulators (which loses
HIDAPI features — gyro, rumble, battery, touchpad) while still delivering
**correct** controller mappings to every emulator, whether it links SDL2
or SDL3. One wizard capture must serve all consumers.

The current workaround lives at `regmsg .../launcher/commands.rs` — it
sets `SDL_JOYSTICK_HIDAPI=0` for every emulator without a `keep_hidapi`
flag, pushing SDL2 emulators onto the joydev backend so they match a
joydev gamecontrollerdb row. This design replaces that.

## 2. Why this is hard — the empirical findings

All measured on RP5 (sm8250) with two purpose-built probes cross-compiled
against the target's own SDL2 (2.32.10) and SDL3 (3.2.30):
`SDL_GameControllerGetBindForButton` / `SDL_GetGamepadBindings` reveal the
resolved binding for each button without needing live input. Methodology
is reproducible — see §8.

### 2.1 SDL joystick-GUID byte layout and match rules

```
byte:  0  1 | 2  3 | 4 5 | 6 7 | 8 9 | 10 11 | 12 13 | 14 | 15
       bus  | crc  | vendor| 0  |product| 0   |version | sig| data
```
- **sig (byte 14):** `0x00` = joydev/evdev backend, `0x68` (`'h'`) = HIDAPI.
- SDL's mapping match (`SDL_PrivateMatch{Controller,Gamepad}MappingForGUID`):
  - **bus (byte 0–1): HARD** — must match, never masked.
  - **sig (byte 14): HARD** — must match.
  - crc (byte 2–3): zeroed before compare, re-matched via the body `crc:` token (soft).
  - version (byte 12–13): soft — exact preferred, falls back to 0.

Source: `SDL_joystick.c::SDL_CreateJoystickGUID`; joydev stamps sig `0`
(`linux/SDL_sysjoystick.c`), HIDAPI stamps `'h'`
(`hidapi/SDL_hidapijoystick.c`).

### 2.2 The core divergence

For a HIDAPI-claimed pad, **SDL2 and SDL3 present the same physical
controller differently:**

| | SDL2-HIDAPI | SDL3-HIDAPI |
|---|---|---|
| dpad | **buttons b11–b14** | **hat h0** |
| `NumHats` | 0 | 1 |
| extra buttons (touchpad/misc) | b15+ | b11+ |

### 2.3 Collision depends on the transport

- **Bluetooth:** SDL2-HIDAPI normalizes the bus byte to `03` (USB), SDL3
  keeps `05` (BT) → GUIDs differ → no collision; each major routes to its
  own row/built-in.
- **USB:** both use bus `03` → **byte-identical GUID, different required
  body → genuine collision.** Proven: injecting an SDL3 hat-row
  (`dpup:h0.1`) into an SDL2-HIDAPI process bound the dpad to **HAT 0 on a
  pad with `NumHats=0`** → dead dpad, while the same row worked under SDL3.

  > A single `gamecontrollerdb.txt` row therefore **cannot** be correct for
  > both SDL2-HIDAPI and SDL3-HIDAPI on a USB controller. The GUID cannot
  > discriminate them; only the **consuming process's SDL major** can.

### 2.4 joydev is uniform across majors — except Nintendo-label pads

The joydev row (sig `0`) resolves identically under SDL2 and SDL3 for
positional pads (PlayStation, etc.). For **Nintendo-label** pads (e.g.
PowerA), SDL2 and SDL3 *built-ins* swap a/b and x/y via
`hint:SDL_GAMECONTROLLER_USE_BUTTON_LABELS`. An **explicit, hint-free**
wizard row (every `a:bN` spelled out) eliminates this — both majors honor
explicit bindings literally.

### 2.5 SDL2-HIDAPI is a deterministic transform of SDL3-HIDAPI

Across DS4, PS5, PowerA, ShanWan the base 11 buttons (indices 0–10:
a,b,x,y,back,guide,start,leftstick,rightstick,leftshoulder,rightshoulder)
are identical. SDL2 only differs by spending button slots 11–14 on the
dpad (SDL3 uses a hat) and shifting extras by +4. Hence:

```
transform_h3_to_h2(row):
  GUID:  bytes[0..2] = 0x0003           # bus → USB-normalized
         (crc, vendor, product, version, sig='h' unchanged)
  dpad:  dpup:h0.1 → dpup:b11
         dpdown:h0.4 → dpdown:b12
         dpleft:h0.8 → dpleft:b13
         dpright:h0.2 → dpright:b14
  shift: every remaining `b<n>` with n >= 11  →  b<n+4>   (touchpad, misc*)
  axes/sticks/triggers: unchanged
```
Verified: DS4 `touchpad b11→b15`; PS5 `touchpad b11→b15, misc1 b12→b16`;
PowerA `misc1 b11→b15`; ShanWan `touchpad b11→b15`. The constant `11` is
structural to SDL's `SDL_GamepadButton` enum (DPAD_UP is the 12th entry).

Because the wizard runs under SDL3, it cannot *observe* SDL2-HIDAPI indices
directly — so it **computes** Row H₂ from the SDL3 capture via this transform
(C++ `serialiseSdl2` in `InputConfig::writeToFile`) and **stores** it. The
transform is a hardware-verified heuristic, not a universal proof: exotic
HIDAPI drivers (Steam, Wii, GameCube adapter, Elite paddles, JoyCons) may not
follow the "base-11 + dpad-at-11 + extras-shift" law. It only ever applies to
user-remapped HID pads under SDL2-HIDAPI (unmapped pads use SDL2's correct
built-in). Storing Row H₂ in a file keeps it inspectable/hand-fixable, and the
same file is a drop-in slot for a future live-SDL2-capture helper (a separate
SDL2 process — SDL2 cannot link into the SDL3 frontend, `SDL_Init` clashes)
should an exotic pad ever need ground truth.

### 2.6 Controller taxonomy (6 pads measured)

| pad | kernel driver | hidraw? | gets `'h'` GUID? | in SDL built-in DB? | USB ①/② collide | joydev maj-uniform | rows the wizard writes |
|---|---|---|---|---|---|---|---|
| PDP Xbox One | `xpad` | no | no | yes | n/a | yes | **1** (joydev) |
| THEC64 THEGamepad | `hid-generic` | yes | **no** (unknown VID) | **no** → unmapped | n/a | yes | **1** (joydev), wizard **mandatory** |
| DS4 / PS5 DualSense | `hid-playstation` | yes | yes | yes | **yes** | yes | HIDAPI + joydev |
| PowerA (Switch) | `hid-generic` | yes | yes | yes | yes | **no** (label swap) | HIDAPI + **explicit** joydev |
| ShanWan clone | `hid-generic` | yes | yes | yes (guessed PS layout) | yes | yes | HIDAPI + joydev |

Decision rule, from one probe: **does opening the pad with HIDAPI on yield
a sig-`'h'` GUID?** No (xpad / unknown-VID HID) → one joydev row, done.
Yes → HIDAPI row + joydev row; make the joydev row explicit; deliver the
SDL2-vs-SDL3 HIDAPI variant per emulator.

### 2.7 The community DB is a joydev DB

`SDL_GameControllerDB/gamecontrollerdb.txt` (REG-Linux fork, "2.0.16
format"): 807 rows, **788 sig `00`**, only **2 sig `'h'`** (both
SDL2-flavored), **0 `crc:` tokens**. The discriminator is the **sig
byte**, not dpad style (102 button-dpad rows are sig `00`, hardware-driven).
⇒ inject community rows in the joydev lane freely; **route sig-`'h'`
community rows to the SDL2 lane** (`-SDL2.txt`) rather than the main file —
SDL built-in HIDAPI covers those pads correctly per major, and a stale
SDL2-flavored `'h'` row in the main file would break SDL3 over USB. This
routing is now done by the fork CI's lane split (§3.1), not an install strip.

## 3. Design

### 3.1 System DB package (`gamecontrollerdb.mk`, this repo)

The two lanes are split **upstream in the fork's CI**, not at install time.
`REG-Linux/SDL_GameControllerDB/.github/workflows/gamecontrollerdb.yaml` runs
daily (and on `add_gamecontrollerdb.txt` push) and:

1. appends `add_gamecontrollerdb.txt` to the upstream `mdqinc` DB;
2. keeps **Linux only**, field-anchored on the `,platform:NAME,` token (drops
   explicit Windows/Mac/Android/iOS rows; keeps Linux rows *and* custom rows
   that omit a platform field — so a controller merely *named* "…Windows…" is
   no longer dropped);
3. **splits** the SDL2-HIDAPI lane out using the discriminator *driver-sig
   `'h'` (`68` at GUID chars 29–30) **AND** dpad-as-buttons*; everything else
   (joydev sig `0`, and SDL3-HIDAPI = sig `'h'` + dpad-as-hat) stays in the
   main file;
4. de-duplicates **each lane** by GUID, keeping the last (so a custom row wins,
   and a USB Row H₂/Row H₃ pair — which share a GUID — never evict each other);
5. commits both files:
   - `gamecontrollerdb.txt` — joydev + SDL3-HIDAPI;
   - `gamecontrollerdb-SDL2.txt` — SDL2-HIDAPI.

The package therefore just **copies both files verbatim** to
`/usr/share/regstation/` — no install-time strip. (`GAMECONTROLLERDB_VERSION`
must point at a commit produced by the updated CI.) Curated REG-Linux HIDAPI
additions go into the single `add_gamecontrollerdb.txt` as an SDL3(hat) +
SDL2(buttons) pair; the CI routes each half to the right file by the
discriminator above. There is no separate `add_gamecontrollerdb_SDL2.txt`
input any more.

- **Stop installing `evmapy_mappings.json`** — it is already dead: REG-Station
  no longer writes the sidecar (`InputConfig.cpp`, `InputManager.cpp`), and
  `regmsg .../evmapy/overrides.rs` derives the same data from the joydev row
  + `/sys/class/input/eventN/device/capabilities/key`. Nothing reads it.

Note: the joydev rows that `evmapy/overrides.rs` consumes are **kept**, so
evmapy is unaffected.

### 3.2 Wizard (REG-Station `InputConfig::writeToFile`)

The wizard owns the transform; the launcher stays dumb. Required behaviour:

1. **Capture with `SDL_JOYSTICK_HIDAPI=1`** so HID-family pads yield the
   SDL3-HIDAPI view (sig `'h'`, dpad-as-hat). The REG-Station launcher /
   service must not disable HIDAPI for the frontend.
2. Per physical connection, write to
   `/userdata/system/configs/regstation/gamecontrollerdb.txt`:
   - **HID-family pad** (runtime GUID sig `'h'`): **Row H₃** (SDL3-HIDAPI,
     as captured) **+ Row J** (joydev, *translated* from kernel cap lists —
     see "Row J derivation" below).
   - **xpad / unknown HID** (runtime GUID sig `0`): **Row J only**.
3. For HID-family pads, also compute **Row H₂** (SDL2-HIDAPI) via the C++
   transform (`serialiseSdl2`: dpad hat → `b11–b14`, button id ≥ 11 shifted
   `+4`, GUID bus → `0x0003`) and **always** write it to the sibling
   **`gamecontrollerdb-SDL2.txt`** — one consistent rule, "SDL2 lane → `-SDL2`
   file". The main file holds only Row H₃ + Row J. (Over USB Row H₂ and Row H₃
   share a GUID so they *must* be in separate files; over Bluetooth their buses
   differ — `03` vs `05` — but Row H₂ still goes to `-SDL2` for consistency,
   and regmsg only feeds `-SDL2` to SDL2 emulators anyway.) The `-SDL2` cleanup
   drops the stale same-connection Row H₂ before re-writing.
4. **Row J is always explicit and hint-free** (kills the Nintendo
   SDL2/SDL3 divergence at the source).
5. GUIDs are **connection-specific** (USB vs BT differ in bus, name-crc,
   and version). Stamp the transport in a trailing comment; ideally prompt
   the user to map both transports. Functionally each connection is its
   own Row H₃ / Row H₂ / Row J.

**Row J derivation (the joydev row is *computed*, not captured).** The wizard
runs under SDL3-HIDAPI, so the captured indices are HIDAPI's synthetic layout
(leftx=0,lefty=1,rightx=2,righty=3,lt=4,rt=5; buttons in SDL gamepad order).
Row J is translated to joydev's kernel-evdev order from the pad's gamepad
sub-device `/sys/class/input/eventN/device/capabilities/{key,abs}` bitmaps:
- **Buttons** → KEY cap list: joydev button N == the Nth `BTN_*` code present.
  Captured per-binding by an evdev probe (`EvdevButtonProbe`) reading the real
  `BTN_*` code that fired; falls back to a standard SDL-positional default
  (`defaultEvdevForSdlName`) when the probe yields nothing.
- **Axes** → ABS cap list: joydev axis N == the Nth `ABS_*` code present.
  `leftx/y → ABS_X/Y`. Sticks/triggers depend on the pad's ABS set:
  **`ABS_RX/RY` present** (hid-playstation) → right stick on `ABS_RX/RY`, analog
  triggers on `ABS_Z/RZ`; **absent** (many Switch-style pads, e.g. BDA NSW,
  which has only `ABS_X/Y/Z/RZ`) → right stick falls to `ABS_Z/RZ` and triggers
  emit as their digital `BTN_TL2/TR2` buttons. A stick that still can't be
  placed is *dropped* rather than emitted with the (colliding) HIDAPI index.

Robustness this required (all hardware-found): capture the evdev `BTN_*` code at
**press** time, not release (a slow/overlapping next press otherwise leaks into
the wrong binding → swapped/duplicate face buttons); select the gamepad evdev
node by its `capabilities/key` advertising `BTN_SOUTH`/`BTN_DPAD_UP` rather than
trusting SDL's device path — over Bluetooth/HIDAPI that path can be a hidraw or
a buttonless motion-sensor/touchpad sibling, which silently produced an
all-defaults (swapped) Row J; and query `defaultEvdevForSdlName` with the
SDL-positional `key` (not the ES name), using a positional `x→BTN_WEST /
y→BTN_NORTH` table.

### 3.3 Launcher (`regmsgd`, `regmsg .../launcher`)

The launcher does **no transform and no per-major rendering** — just a
flavored concat that lets SDL match the right row at runtime.

**Per-emulator metadata** (Lua `module_flag`):
- `sdl3 = true` on the SDL3 generators (amiberry, applewin, dhewm3, dolphin,
  rpcs3, xemu, ymir). Absent ⇒ SDL2. (`jgenesis` has no generator; the
  `regstation` frontend is in-process.)
- `force_joydev = true` (opt-out) for any emulator that mishandles HIDAPI.

**HIDAPI policy:** on by default (gated — see below). For `force_joydev`
emulators set `SDL_JOYSTICK_HIDAPI=0`.

**DB set** (`controllers::read_sdl_db_flavored(append_sdl2)`, in memory —
**never write to read-only `/usr/share`**): system ⊕ user, plus
`gamecontrollerdb-SDL2.txt` **appended last** when `append_sdl2` is set
(`append_sdl2 = !sdl3 && !force_joydev`). Appending last means Row H₂ wins
the same-GUID USB collision via SDL's last-wins rule.

**Injection** (`helpers::sdl_controller_config_all`): emit **every** DB row
whose GUID vendor (chars 8–11) + product (chars 16–19) matches a connected
pad, in file order, into `SDL_GAMECONTROLLERCONFIG`. SDL then routes each
backend to its own row by bus + driver-sig:
- SDL3 emulator (HIDAPI on, no `-SDL2`): pad's `'h'` runtime GUID → Row H₃.
- SDL2 emulator (HIDAPI on, `-SDL2` appended): pad's `'h'` runtime GUID →
  Row H₂ (wins last over Row H₃ on USB; on BT only Row H₂'s bus `03` matches).
- joydev / `force_joydev`: sig-`0` runtime GUID → Row J.
- No user row → SDL's per-major built-in applies (verified correct).

**Rollout gate:** the new path is opt-in via the **`REGMSG_KEEP_HIDAPI`** env
var on `regmsgd` while it is validated on hardware; unset = the legacy
blanket `SDL_JOYSTICK_HIDAPI=0`. Flip to default-on and delete the legacy
branch once validated.

**RetroArch** needs no special case: it is an SDL2 emulator
(`input_joypad_driver=sdl2`), matches Row H₂ via env, `SDL_GameController`
normalizes to the enum, and the stock `autoconfig/sdl2/*.cfg` profiles apply.
(Do **not** switch RetroArch to the `udev` joypad driver — its udev stack has
**no controller gyro**: `udev_input.c` stubs gyro/accel, illuminance-only.
Only the SDL-HIDAPI path exposes DS4/DualSense gyro.)

## 4. Why this meets the goal

- HIDAPI stays **on** for SDL2 and SDL3 → gyro/rumble/touchpad/battery kept.
- Each process gets its own coordinate system: SDL3-HIDAPI verbatim,
  SDL2-HIDAPI derived, joydev for HIDAPI-blind pads.
- One capture → all lanes (wizard writes up to 3 rows: H₃, H₂, J; launcher
  just concatenates and lets SDL match).
- Unmapped recognized pads use correct per-major built-ins (no injection).
- Clones self-correct: the wizard captures what the user actually pressed
  under SDL3-HIDAPI; the transform carries it to SDL2.

## 5. Edge cases & open items

1. **USB↔BT** are distinct GUIDs ⇒ distinct rows. Decide UX (auto-prompt
   both, or map-on-demand).
2. **Fake-DS4 / fake-Switch clones break under HIDAPI-on — even the wizard.**
   A clone that reports a DualShock4-compatible HID descriptor (e.g. the Spirit
   of Gamer SOG-RWPABK / ShanWan `2563:0526` wheel) is claimed by SDL's HIDAPI
   PS4 driver on `hidraw` and presented as a DS4 — but in its fallback "Android"
   mode that hidraw instance emits **no input**, while the real input sits on
   joydev `jsN`. The pad therefore reads dead **even in the wizard** (cannot be
   mapped), and `force_joydev` does NOT help: that flag is per-*emulator*, not
   the frontend. Escape hatch: set **`SDL_HINT_HIDAPI_IGNORE_DEVICES`** (e.g.
   `0x2563/0x0526`) at the **frontend** so SDL skips HIDAPI for that VID/PID and
   uses joydev + the community `ShanWan Gamepad` row; real Sony pads (`054C`)
   are unaffected. Hardware-confirmed on RP5: with the ignore set the SDL probe
   moves the wheel from `/dev/hidraw0` (dead DS4 map) to `/dev/input/eventN`
   (live joydev, `is_gamecontroller=true`). This wants a configurable VID/PID
   ignore-list (a Settings/`system.conf` key the frontend reads), defaulting to
   known fake-DS4 clones. (The older note that an unmapped ShanWan gamepad just
   "gets a phantom touchpad button — benign" only held for clones SDL's HIDAPI
   guess happens to drive correctly; a fake-DS4 whose hidraw is dead is not
   benign.) `force_joydev` remains the escape hatch for the *emulator* side.
3. **Mixed pad types on one process** (a gyro pad wanting HIDAPI + a clone
   wanting joydev): `SDL_JOYSTICK_HIDAPI` is per-process — genuine
   limitation. Default HIDAPI-on; injected rows still correct each pad.
4. **Transform breadth:** validate the wizard's `serialiseSdl2` transform on
   an 8BitDo in Switch/D-input mode before locking (robust by enum structure,
   but cheap to confirm).
5. **`write_sdl_db` file form:** configgen's `write_sdl_db_all_controllers`
   (gap #3 in the migration) wrote a DB *file* for
   `SDL_GAMECONTROLLERCONFIG_FILE`. This design uses the env string and
   does not need it; confirm no generator depends on the file form before
   configgen is removed.

## 6. Implementation status & remaining order

Done:
1. ✅ `REG-Station InputConfig::writeToFile` — `serialiseSdl2` transform +
   Row H₂ writer (sibling `-SDL2.txt` on USB collision, main file on BT) +
   `sdl2CanonForCleanup` cleanup. **Row J derivation hardened + hardware-
   validated** (PS3/PS4/PS5 USB+BT and BDA NSW): ABS-cap axis translation +
   `fullSticks` heuristic (no `ABS_RX/RY` → right stick on `ABS_Z/RZ`, digital
   triggers); `defaultEvdevForSdlName` x/y fix + SDL-positional `key` lookup
   (was producing the a/b swap); press-time evdev capture; gamepad-node
   selection so the probe works over Bluetooth; per-transport version-variant
   cleanup (`padKey`). REG-Station `hidapi` branch (commits 6994b02, 7a0f19b).
2. ✅ `regmsg` — `read_sdl_db_flavored` + `sdl_controller_config_all` (emit all
   vid/pid-matching rows); wired in `commands.rs` behind the **opt-in
   `REGMSG_KEEP_HIDAPI`** toggle with `force_joydev`/`sdl3` flags. Compiles,
   219 tests pass (incl. 4 new).
3. ✅ `sdl3 = true` on the 7 SDL3 generators (amiberry, applewin, dhewm3,
   dolphin, rpcs3, xemu, ymir).
4. ✅ Lane split moved to the fork CI
   (`SDL_GameControllerDB/.github/workflows/gamecontrollerdb.yaml`): appends
   `add_gamecontrollerdb.txt`, field-anchored Linux filter, per-lane GUID
   dedup, and splits SDL2-HIDAPI (sig `'h'` + dpad-as-buttons) into
   `gamecontrollerdb-SDL2.txt`, leaving joydev + SDL3-HIDAPI in the main file
   (validated on the live DB: 804 main rows, 1 SDL2-HIDAPI row extracted, no
   leakage). `gamecontrollerdb.mk` now just copies both files;
   `evmapy_mappings.json` no longer installed (no other consumer in the tree).
   (Bump `GAMECONTROLLERDB_VERSION` to a commit produced by the updated CI.)

Remaining:
5. Device-validate with `REGMSG_KEEP_HIDAPI=1` across the 6 test pads ×
   SDL2/SDL3 emulators using the §8 probe method.
6. Flip the toggle to default-on and delete the legacy force-off branch.
7. **Frontend HIDAPI ignore-list for fake-DS4 clones** (§5.2): set
   `SDL_HINT_HIDAPI_IGNORE_DEVICES` in REG-Station from a configurable key,
   defaulting to include `0x2563/0x0526` (SOG-RWPABK / ShanWan wheel). Not yet
   implemented — confirmed working via the env var on device.

## 7. Components & key files

- `SDL_GameControllerDB/.github/workflows/gamecontrollerdb.yaml` (fork CI) — appends `add_gamecontrollerdb.txt`, Linux filter, per-lane GUID dedup, splits SDL2-HIDAPI into `gamecontrollerdb-SDL2.txt` (§3.1). **Done.**
- `package/controllers/gamecontrollerdb/gamecontrollerdb.mk` — system DB install: copies both pre-split lanes verbatim, drops `evmapy_mappings.json` (§3.1). **Done.**
- `REG-Station/src/input/InputConfig.cpp` (`writeToFile`) — wizard transform +
  Row H₂ writer (`serialiseSdl2`, `sdl2Guid`, `sdl2CanonForCleanup`). **Done.**
- `regmsg/src/bin/daemon/launcher/`:
  - `commands.rs` — HIDAPI policy block, gated `REGMSG_KEEP_HIDAPI` injection. **Done.**
  - `helpers.rs` — `sdl_controller_config_all` + `collect_vid_pid_keys` +
    `filter_db_rows_for_pads` (+ unit tests). **Done.**
  - `controllers.rs` — `read_sdl_db_flavored` (+ `SDL_DB_SDL2_PATH`). **Done.**
  - `lua.rs` — `module_flag` reads `sdl3` / `force_joydev` (no change needed). **Done.**
  - `lua/generators/{amiberry,applewin,dhewm3,dolphin,rpcs3,xemu,ymir}.lua` —
    `sdl3 = true`. **Done.**
  - `evmapy/overrides.rs` — consumes joydev rows (unchanged; keep them in system DB).

## 8. Test methodology (reproducible)

Cross-compile two probes against the target sysroot and run on device:

```
SR=output/<target>/host/aarch64-buildroot-linux-gnu/sysroot
host/bin/aarch64-buildroot-linux-gnu-gcc sdl2probe.c -I$SR/usr/include/SDL2 -D_REENTRANT -L$SR/usr/lib -lSDL2 -o sdl2probe
host/bin/aarch64-buildroot-linux-gnu-gcc sdl3probe.c -I$SR/usr/include   -D_REENTRANT -L$SR/usr/lib -lSDL3 -o sdl3probe
# on device, per pad, for HIDAPI in {1,0}:
SDL_JOYSTICK_HIDAPI=$H SDL_GAMECONTROLLERCONFIG="<row>" ./sdlNprobe
```
Each probe prints, per joystick: runtime GUID, `NumButtons/NumHats/NumAxes`,
the active mapping string, and the resolved input binding for each
face/dpad button. Stop the REG-Station frontend only for live-input tests;
static binding queries are unaffected by it (hidraw allows concurrent opens).

## Appendix A — measured mapping lines (DualSense, reference)

USB (collision case, ① and ② share a byte-identical GUID):

```
# ① SDL2-HIDAPI  (btn=17 hat=0, dpad=buttons)
030057564c050000e60c000000016800,*,a:b0,b:b1,x:b2,y:b3,back:b4,guide:b5,start:b6,leftstick:b7,rightstick:b8,leftshoulder:b9,rightshoulder:b10,dpup:b11,dpdown:b12,dpleft:b13,dpright:b14,touchpad:b15,misc1:b16,leftx:a0,lefty:a1,rightx:a2,righty:a3,lefttrigger:a4,righttrigger:a5,crc:5657,platform:Linux
# ② SDL3-HIDAPI  (btn=13 hat=1, dpad=hat) — SAME GUID as ①
030057564c050000e60c000000016800,*,a:b0,b:b1,x:b2,y:b3,back:b4,guide:b5,start:b6,leftstick:b7,rightstick:b8,leftshoulder:b9,rightshoulder:b10,dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,touchpad:b11,misc1:b12,leftx:a0,lefty:a1,rightx:a2,righty:a3,lefttrigger:a4,righttrigger:a5,crc:5657,platform:Linux
# ③ joydev (SDL2 == SDL3)  (sig 00)
0300d0424c050000e60c000011810000,PS5 Controller,a:b0,b:b1,x:b3,y:b2,back:b8,guide:b10,start:b9,leftshoulder:b4,rightshoulder:b5,leftstick:b11,rightstick:b12,dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,leftx:a0,lefty:a1,rightx:a3,righty:a4,lefttrigger:a2,righttrigger:a5,platform:Linux
```
① = `transform_h3_to_h2(②)`: dpad hat→b11–14, `touchpad b11→b15`,
`misc1 b12→b16`, bus already `03`.
