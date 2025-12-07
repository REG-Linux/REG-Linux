# libretro-prboom

ARM-oriented Doom core packaged for libretro frontends.

## Build notes
- **Version:** commit `b3e5f8b2e8855f9c6fc7ff7a0036e4e61379177d` (Dec 2024).
- **Config:** needs a C++ toolchain and selects the `libretro-prboom` config.
- **Build system:** invokes the upstream `Makefile` with `platform` set to `armv`, `armv neon`, or `unix` depending on the target board, and uses `GIT_VERSION` stamping inside the make invocation.
- **Install:** copies `prboom_libretro.so` to `/usr/lib/libretro`.
