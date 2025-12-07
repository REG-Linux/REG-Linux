# libretro-reminiscence

Libretro wrapper around the Flashback reimplementation.

## Build notes
- **Version:** commit `e21856941dcedee23026da8b2ca94708c14dae7f` (Jan 2024).
- **Config:** selects the `BR2_PACKAGE_LIBRETRO_REMINISCENCE` config (C++ toolchain).
- **Build system:** upstream Makefile builds the core for the detected platform and installs `reminiscence_libretro.so` into `/usr/lib/libretro`.
