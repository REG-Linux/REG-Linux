# Libretro Beetle PC-FX

The `libretro-beetle-pcfx` core runs the PC-FX emulator inside REG-Linux’s libretro stack for ARM builds.

## Build notes

- `Version`: f559b8f4e1d72af43537260ee9335556b4a424b8
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-makefile.patch`
