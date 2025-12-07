# libretro-mrboom

Builds the Mr. Boom core (`mrboom_libretro.so`) for libretro frontends.

## Build notes
- **Version:** 5.5 release (May 2024) from `Javanaise/mrboom-libretro` with submodules.
- **Config:** requires a C++ toolchain and conditionally defines `HAVE_NEON=1` on NEON-capable ARM targets; `SKIP_GIT=1` avoids git commands during cross-build.
- **Build system:** runs the upstream Makefile via `$(generic-package)` and installs the shared object under `/usr/lib/libretro`.
