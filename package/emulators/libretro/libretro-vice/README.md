# Libretro VICE (xscpu64)

The `libretro-vice` core compiles every Commodore 8-bit binary (x64, x128, xvic, xplus4, xpet, xcbm2, x64dtv, x64sc, xscpu64) so REG-Linux ships the full VICE family from libretro.

## Build notes

- `Version`: e9f8ac034ddef3025f0567768f7af8219f7cfdb8
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`, plus `BR2_PACKAGE_LIBRETRO_VICE`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-lto.patch` and `000-makefile.patch`
