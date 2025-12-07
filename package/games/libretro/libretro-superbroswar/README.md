# libretro-superbroswar

Super Mario War core for libretro deliverables.

## Build notes
- **Version:** commit `d8d5d58f3cbc1e08f91a0e218bc990ec47282c08` (Oct 2024) from `libretro/superbroswar-libretro` with `git submodules`.
- **Config:** standard C++ toolchain requirement; the recipe sets `-fPIC` flags through the environment.
- **Build system:** builds via the upstream `Makefile.libretro` inside the source tree and installs `superbroswar_libretro.so` into `/usr/lib/libretro`. A patch (`001-fix-gcc14.patch`) updates the build for modern gcc versions.
