# libretro-zc210

Zelda Classic core packaged for the libretro stack.

## Build notes
- **Version:** commit `b6426da40b074245fda097fd345fa7c9cdbf152a` (April 2022).
- **Config:** selects the `libretro-zc210` option requiring a C++ toolchain.
- **Build system:** runs the Makefile with `platform="unix"` and includes a `GIT_VERSION` token; installs `zc210_libretro.so` into `/usr/lib/libretro`.
