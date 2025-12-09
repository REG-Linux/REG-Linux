# Libretro PUAE

The `libretro-puae` core packs the Amiga emulator into REG-Linux’s libretro stack, keeping the distro’s build and capsimage patches.

## Build notes

- `Version`: f1c248602abb58e7c570feec3f59f4677407b252
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `002-isoc99math.patch`, `001-capsimg-path.patch`, `003-fix-gcc14.patch`, `000-makefile.patch`
