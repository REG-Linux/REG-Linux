# Libretro PicoDrive

The `libretro-picodrive` core brings Sega Mega Drive/SMS emulation into REG-Linux’s libretro catalog with the libpng, gcc14, and flto patches already applied.

## Build notes

- `Version`: v2.05
- `Dependencies`: `BR2_PACKAGE_LIBPNG`, `BR2_INSTALL_LIBSTDCPP`, and `!BR2_INSTALL_LIBSTDCPP && !BR2_PACKAGE_LIBPNG`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-gcc14-fix.patch`, `002-flto-auto.patch`, `000-makefile.patch`
