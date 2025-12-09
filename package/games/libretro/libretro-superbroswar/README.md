# Libretro Super Bros War

The `libretro-superbroswar` core wraps the Super Mario War reimplementation for REG-Linux, including the `001-fix-gcc14.patch` needed for newer GCC releases.

## Build notes

- `Version`: `d8d5d58f3cbc1e08f91a0e218bc990ec47282c08` (Oct 2024) from `libretro/superbroswar-libretro`.
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, `-fPIC` enforced across targets.
- `Build helper`: Generic/Makefile (`generic-package`) building via `Makefile.libretro` and installing `/usr/lib/libretro/superbroswar_libretro.so`.
