# Libretro MAME2010

The `libretro-mame2010` core keeps REG-Linux’s ARM arcade catalog aligned with the 2010-era MAME release plus the Raspberry Pi patch set.

## Build notes

- `Version`: c5b413b71e0a290c57fc351562cd47ba75bac105
- `Dependencies`: `BR2_PACKAGE_ZLIB`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-rpi_makefile.patch`
