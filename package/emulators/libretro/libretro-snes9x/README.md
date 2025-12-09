# Libretro Snes9x

The `libretro-snes9x` core ports Snes9x into REG-Linux’s libretro catalog, keeping FLTO, Raspberry Pi tuning, and MSU1 fixes active.

## Build notes

- `Version`: 49f484569ff2aec7ff08e7598a97d6c9e6eae72d
- `Dependencies`: `BR2_PACKAGE_ZLIB`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `002-enable-flto-auto.patch`, `001-RPi5-tuning.patch`, `003-enable-zip-msu1.patch`, `004-hack-zip-msu1-fixup.patch`
