# fteqw

FTEQW is a heavily extended, actively maintained fork of the original idTech1
Quake engine lineage. Upstream: https://github.com/fte-team/fteqw

Replaces `quakespasm` and `libretro-tyrquake` as this tree's Quake 1 engine.
Unlike those two, it is a single binary that also natively plays Hexen II
(and, per upstream docs, Quake II using the original `game.so`/`.dll` and a
partial Quake III with no mission-pack/mod support -- neither of those is
wired up by this package; Quake II stays on `yquake2`, Quake III stays on
`ioquake3`).

## Build

Built via CMake (`-DFTE_DEP_SDL3=ON`), not the legacy top-level `Makefile`.
The Makefile's generic Linux target auto-detects EGL/Wayland support by
`wildcard`-checking `/usr/include/EGL/egl.h` on the *build host*, which
breaks under cross-compilation. The CMake build's SDL3 path sidesteps this
entirely: it doesn't even compile the EGL glue (`engine/gl/gl_videgl.c`) --
SDL3 itself picks GL, GLES, or Vulkan for whatever it was built with, so
this one binary runs across this tree's GL and GLES-only targets alike.

Most dev tools (`iqmtool`, `qtv`, ...) and plugins unrelated to Quake1/
Hexen2 (the Quake III plugin, Call of Duty, Bullet/ODE physics) are
disabled -- see `fteqw.mk` for the full `FTE_CONF_OPTS` list. `fteqcc`
(the QuakeC compiler) has to stay enabled despite not being shipped: the
`menusys`/`csaddon` CMake targets are built unconditionally (`ALL`) and
invoke it internally to compile the engine's own bundled QuakeC content
(`menusys.pk3`, `csaddon.pk3`) -- disabling it breaks the main build.

Six patches were needed, all real upstream oversights rather than
anything specific to this package:
- `000-no-march-native-cross-compile.patch`: upstream unconditionally
  appends `-march=native`/`-mcpu=native` for GCC, which only makes sense
  for a native (non-cross) build; skip it under `CMAKE_CROSSCOMPILING`
  (already used elsewhere in the same file for an unrelated MinGW issue).
- `001-disable-hardcoded-gnutls.patch`: `-DFTE_DEP_GNUTLS=OFF` only
  controls whether CMake links gnutls -- `engine/common/config_fteqw.h`
  separately hardcodes `#define HAVE_GNUTLS //on linux` regardless of
  that option, so `net_ssl_gnutls.c` still tried to `#include
  <gnutls/gnutls.h>` and failed. Neither toggle is aware of the other.
- `002-fix-zlib-z_crc_t-type-mismatch.patch`: `fs_zip.c` falls back to
  `#define z_crc_t uLongf` whenever zlib's own `Z_U4` detection macro
  isn't defined -- but this zlib no longer defines `Z_U4` at all (it just
  unconditionally `typedef`s its own correctly-sized `z_crc_t` as
  `unsigned int` in `zconf.h`), so the `#ifndef Z_U4` is always true and
  the fallback clobbers the real typedef with a stale 8-byte-on-LP64
  `uLongf` assumption. `get_crc_table()` still returns the real zlib's
  `unsigned int *`, so assigning it to the wrongly-retyped `uLongf *`
  field is a hard `-Wincompatible-pointer-types` error on GCC 14+ (a
  warning on older GCC).
- `003-gles-fallback-when-no-desktop-opengl.patch`: `GLQUAKE` (the
  compile-time switch for the entire GL renderer, `engine/gl/gl_vidsdl.c`
  and friends) only gets defined when CMake's `FIND_PACKAGE(OpenGL)`
  finds *desktop* GL/GLX -- which doesn't exist at all on GLES-only mesa3d
  builds (Panfrost/freedreno/lima/etc, no `GL/gl.h` anywhere in the
  sysroot). Confirmed on real hardware (CHA/H3): the engine still built
  and ran, but with zero renderers compiled in (Vulkan headers aren't a
  build dependency either), so it silently fell back to the
  video-less "dedicated" stub every time -- no build error, no crash, just
  a black screen. The SDL3 path never links against libGL/libGLESv2
  directly (every GL entrypoint is resolved at runtime via
  `SDL_GL_GetProcAddress`), so this only needed a header fallback: if no
  desktop GL is found but `GLES2/gl2.h` is, define `GLQUAKE` + a new
  `FTE_GLES` switch that picks the GLES2 header in `glquake.h`, mirroring
  the engine's existing Android/Emscripten GLES2-only branches exactly.
  Needs `FTEQW_DEPENDENCIES += libgles` (below) to actually find those
  headers -- under `BR2_PER_PACKAGE_DIRECTORIES`, a package's build only
  sees headers from packages it depends on, regardless of what's staged
  system-wide.
- `004-gles-define-glesonly.patch`: getting `GLQUAKE`/`FTE_GLES` defined
  (003, above) wasn't enough by itself -- confirmed on real hardware
  (CHA/H3): `engine/gl/gl_backend.c`'s `GLBE_Init()` still tried to query
  `GL_STENCIL` via `glGetFramebufferAttachmentParameteriv`, a desktop-GL-
  only enum that doesn't exist in `GLES2/gl2.h`, because that whole
  desktop-only codepath is only excluded when `GLESONLY` is defined --
  and nothing defined it for this new `FTE_GLES` build path (only the
  existing `ANDROID`/`FTE_TARGET_WEB` branches in `bothdefs.h` did). Six
  files across the engine gate on this same single macro
  (`gl_backend.c`, `gl_vidcommon.c`, `shader.h`, `common.c`, `m_mp3.c`,
  `bothdefs.h` itself), so defining it once for `FTE_GLES` -- mirroring
  the `ANDROID` block, minus its unrelated `NO_FREETYPE`/`NO_OPENAL`
  side effects, which this package doesn't want -- covers all of them.
- `005-no-x11-for-sdl3-vulkan-surface.patch`: confirmed on real hardware
  (odroidc5, which has `BR2_PACKAGE_REGLINUX_VULKAN` and thus
  `vulkan-headers`, unlike CHA): `engine/vk/vkrenderer.h` unconditionally
  enables `VK_USE_PLATFORM_XLIB_KHR`/`VK_USE_PLATFORM_XCB_KHR` on any
  generic Linux build unless `NO_X11` is defined, pulling in
  `xcb/xcb.h` as a hard compile-time requirement ("fatal error:
  xcb/xcb.h: No such file or directory") that isn't declared as a build
  dependency anywhere. This hand-rolled XLIB/XCB Vulkan surface code is
  redundant on the SDL3 path used here regardless -- SDL3 creates
  Vulkan surfaces itself (`SDL_Vulkan_CreateSurface`), so `bothdefs.h`
  now defines `NO_X11` whenever `FTE_SDL3` is set, which is already
  unconditionally true for every board using this package.

`FTEQW_DEPENDENCIES` also pulls in `libgles` unconditionally (safe
everywhere -- every board here already selects
`BR2_PACKAGE_HAS_LIBGLES`) and `vulkan-headers` when
`BR2_PACKAGE_REGLINUX_VULKAN` is set (the same flag flycast/xemu/etc.
gate their own Vulkan support on). `vulkan-headers` makes
CMakeLists.txt's own existing (and previously dead)
`FIND_PATH(VULKAN_INCLUDE_DIR vulkan/vulkan.h) -> VKQUAKE` check
actually succeed on Vulkan-capable boards (odroidc5, sm8250,
x86_64_v3, ...), giving FTE a real second renderer choice alongside
GLES. Boards without `BR2_PACKAGE_REGLINUX_VULKAN` (CHA and other
older/32-bit targets) just don't get `VKQUAKE` compiled in at all --
same as before this dependency was added.

There's also a `host-fteqw` package in this same `.mk` (same source,
`FTE_TOOL_QCC` only): the `menusys`/`csaddon` CMake targets invoke a bare
`fteqcc` expecting to find it on `PATH`, but the *target* build's fteqcc
is cross-compiled for the device and can't run on the build host at all
("fteqcc: not found"). `host-fteqw` builds a host-native fteqcc instead,
staged onto `PATH` automatically as an `FTEQW_DEPENDENCIES` entry (same
mechanism that makes `host-cmake`/`host-pkgconf` available to any
package's build) -- same idea as `HOST_OPENRCT2` in `openrct2.mk`.

## Install layout

Unlike `ioquake3`/`yquake2`, the binary itself is **not** datainit'd --
it's installed straight to `/usr/bin/fteqw` as a normal system binary.
One binary serves any of the engine's built-in game profiles (which game
it runs is purely a runtime `-quake`/`-hexen2`/... flag choice), and it
carries no per-game or per-mod native code (mission packs/mods are plain
QuakeC bytecode the engine interprets, not compiled `.so`s like Quake
II's) -- so it has no reason to wait on, or live alongside, the user's
ROM data the way the datainit pattern exists for.

What *is* datainit'd is the ROM folder skeleton: empty `roms/quake` and
`roms/hexen2` directories, so first-boot populate
(`board/fsoverlay/etc/init.d/S12populateshare`) creates
`/userdata/roms/quake` and `/userdata/roms/hexen2` for the user to drop
their own `id1`/`hipnotic`/`rogue` (Quake) or `data1`/`portals`
(Hexen II) `.pak` data into.

## Launching

Always pass `-basedir` explicitly -- without it, FTE defaults to the
process's current working directory (`realpath(".")`), not the binary's
own location, which is fragile to rely on from a launcher.

```
fteqw -quake -basedir /userdata/roms/quake -nohome ...
fteqw -hexen2 -basedir /userdata/roms/hexen2 -nohome ...
```

`-nohome` (like yquake2's `-portable`) keeps config/saves next to
`-basedir` instead of a separate home directory.

Built-in game profiles relevant here (from `common/fs.c`'s
`gamemode_info[]` table), each naming the data subdirectory expected
inside `-basedir`:

| Flag | Data dir | Game |
|---|---|---|
| `-quake` | `id1/` | Quake (also checks `qw/`) |
| `-hipnotic` | `hipnotic/` (on top of `id1/`) | Quake: Scourge of Armagon |
| `-rogue` | `rogue/` (on top of `id1/`) | Quake: Dissolution of Eternity |
| `-hexen2` | `data1/` | Hexen II |
| `-portals` | `portals/` (on top of `data1/`) | Hexen II: Portals of Praevus |

## Controllers

No custom binds are required for basic play -- FTEQW ships sensible
built-in gamepad defaults (`client/keys.c`'s `defaultedbind` switch):
right trigger fires (`+attack`), left shoulder jumps, A cycles weapons
(`impulse 10`), D-pad and both analog sticks drive movement/look via the
engine's own axis handling (`client/in_generic.c`), left stick click
crouches. These need no per-launch config from regmsgd -- unlike
`yquake2`, which shipped with no gamepad defaults at all and needed a full
`autoexec.cfg` written per launch.

If a future regmsg generator wants to override specific buttons, the
bind-able names (`client/keys.c`'s keyname table) are: `GP_A`, `GP_B`,
`GP_X`, `GP_Y`, `GP_BACK`, `GP_START`, `GP_GUIDE`, `GP_LSHOULDER`,
`GP_RSHOULDER`, `GP_LTRIGGER`, `GP_RTRIGGER`, `GP_LTHUMB`, `GP_RTHUMB`,
`GP_DPAD_UP`, `GP_DPAD_DOWN`, `GP_DPAD_LEFT`, `GP_DPAD_RIGHT`.

## Status

Builds cleanly for sm8250. Launcher wiring is in place: `es_systems.yml`
(`quake`, `hexen2` systems, `.quake`/`.hexen2` ROM extensions),
`launcher-defaults.yml` (both point at `emulator: fteqw`), and the
`fteqw`/`fteqw.lua` generator + `keys/fteqw.json` evmapy hotkeys in the
`regmsg` repo (branch `fteqw`). ROM data for testing goes under
`roms/quake/` and `roms/hexen2/`.

Not yet hardware-tested: controller defaults, menu navigation, renderer/
resolution selection, and mission-pack/mod `-game`/named-flag parsing are
all based on source research (see the Controllers section above and
upstream's `common/fs.c` `gamemode_info[]` table), same as the ioquake3/
yquake2 generators before their first real device test.
