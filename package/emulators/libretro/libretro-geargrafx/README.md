# Libretro Geargrafx

The `libretro-geargrafx` core supplies REG-Linux with the Geargrafx Commodore 8-bit emulator, including the libc/Makefile fixes needed for Musl.

## Build notes

- `Version`: 1.6.4
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-fix-libchdr-musl.patch` and `000-makefile-additions.patch`
