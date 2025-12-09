# Libretro FCEUmm

The `libretro-fceumm` core lets REG-Linux run the FCEUmm NES emulator with the Raspberry Pi tuning already in place.

## Build notes

- `Version`: 5cd4a43e16a7f3cd35628d481c347a0a98cfdfa2
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-RPi5-tuning.patch` and `002-enable-lto.patch`
