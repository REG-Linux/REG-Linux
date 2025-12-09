# Libretro Geolith

The `libretro-geolith` core offers Neo Geo AES/MVS emulation inside REG-Linux’s libretro stack with the Musl/Makefile fixes already applied.

## Build notes

- `Version`: 96b2b5fd4ef9f205bc5e23cb7dbf123e04e13de0
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-makefile.patch`
