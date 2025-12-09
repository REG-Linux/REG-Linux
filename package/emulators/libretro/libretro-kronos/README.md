# Libretro Kronos

The `libretro-kronos` core delivers Sega Saturn emulation to REG-Linux with optional GL/GLES paths and the standard set of glu/BIOS patches.

## Build notes

- `Version`: 2.7.0_official_release
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, `(BR2_PACKAGE_HAS_LIBGL || BR2_PACKAGE_HAS_LIBGLES)`, and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `002-libretro-2.7.0-cumulative-patches.patch`, `000-biospath.patch`, `001-makefile.patch`
