# libretro-tyrquake

Quake I core that selects the proper RPi target and stamps the git version.

## Build notes
- **Version:** commit `9dcc3ff4ccf96d2f7aa029b738f2c90685b9257f` (Dec 2024).
- **Config:** C++ toolchain requirement; the detected platform varies from `armv` to `rpi5_64` or `unix`.
- **Build system:** upstream Makefile triggered with `platform=$(LIBRETRO_TYRQUAKE_PLATFORM)` and sanitized `GIT_VERSION`; installs `tyrquake_libretro.so`.
