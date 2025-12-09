# Libretro Beetle PSX

The `libretro-beetle-psx` core brings PlayStation 1 emulation into REG-Linux’s libretro catalog with Raspberry Pi tuning and the CD-less Makefile adjustments.

## Build notes

- `Version`: b8dd9de6dba5fa0359c0a7df7f0b61a7fc503093
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-RPi5-tuning.patch` and `000-makefile-no-cd.patch`
