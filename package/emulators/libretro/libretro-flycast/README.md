# Libretro Flycast

The `libretro-flycast` core runs Dreamcast/Naomi/Atomiswave emulation with the OpenMP and GL/GLES hooks REG-Linux enables for ARM/x86 targets.

## Build notes

- `Version`: `$(FLYCAST_VERSION)`
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, `BR2_GCC_ENABLE_OPENMP`, `(BR2_PACKAGE_HAS_LIBGLES || BR2_PACKAGE_HAS_LIBGL)`, and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `000-makefile-additions.patch`
