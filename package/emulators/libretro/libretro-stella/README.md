# Libretro Stella

The `libretro-stella` core adds Atari 2600 emulation into REG-Linux’s libretro stack with FLTO and Raspberry Pi makefile tweaks.

## Build notes

- `Version`: 7.0
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-makefile-flto-auto.patch` and `000-rpi_makefile.patch`
