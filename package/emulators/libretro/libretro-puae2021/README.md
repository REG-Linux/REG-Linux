# Libretro PUAE 2021

The `libretro-puae2021` core updates REG-Linux’s Amiga library with the 2021 libretro-uae stack and the usual Raspberry Pi/build fixes.

## Build notes

- `Version`: 71d105288333ce63aeaaa20ebb1dfe07c24d050f
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-rpi_makefile.patch`, `002-isoc99math.patch`, `001-capsimg-path.patch`, `003-gcc14-hack.patch`
