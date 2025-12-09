# Libretro EightyOne

The `libretro-81` core runs the ZX81 (EightyOne) emulator inside REG-Linux’s libretro stack, including REG-Linux-specific key handling.

## Build notes

- `Version`: ffc99f27f092addc9ddd34dd0e3a3d4d1c053cbf
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `zx81.keys` into `/usr/share/evmapy` (or equivalent) and applies `001-slowerkeyboard.patch`, `000-rpi_makefile.patch`
