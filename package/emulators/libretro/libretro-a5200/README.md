# Libretro Atari 5200

The `libretro-a5200` core runs the Atari 5200 emulator under REG-Linux’s libretro setup, including Raspberry Pi optimizations.

## Build notes

- `Version`: 526404072821bb2021fab16f8c5dbbca300512c8
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-RPi5-optimisation.patch`
