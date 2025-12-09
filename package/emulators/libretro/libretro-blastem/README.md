# Libretro BlastEm

The `libretro-blastem` core runs Sega 16-bit titles through REG-Linux’s libretro layer while keeping the CPU and VDP fixes required for modern toolchains.

## Build notes

- `Version`: 842de15d6b59
- `Dependencies`: allows both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies REG-Linux patches (`000-force-newcore-noarch.patch`, `002-fix-cpu-dsl.patch`, `003-fix-vdp-nothread.patch`, `001-fix-gcc14-error.patch`)
