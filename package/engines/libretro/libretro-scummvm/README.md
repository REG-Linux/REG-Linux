# libretro-scummvm

ScummVM built as a libretro core via `backends/platform/libretro`. Upstream: https://github.com/scummvm/scummvm

`libretro-deps` and `libretro-common` are cloned at pinned commits during a pre-configure hook because the upstream build system requires them in-tree. The platform string is set per-board (e.g. `rpi1`, `rpi4_64`, `unix`); desktop GL is currently forced off in favour of GLES2 on all targets pending a GL fix. The output is `scummvm_libretro.so` under `/usr/lib/libretro/`.
