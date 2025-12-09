# Libretro Atari800

`libretro-atari800` provides Atari800 and Atari5200 emulation for REG-Linux’s libretro frontend, offering RPi build tweaks.

## Build notes

- `Version`: 6a18cb23cc4a7cecabd9b16143d2d7332ae8d44b
- `Dependencies`: supports either `BR2_INSTALL_LIBSTDCPP` or `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-rpi_makefile.patch`
