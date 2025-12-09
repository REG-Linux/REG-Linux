# Libretro GPsp

The `libretro-gpsp` core runs the Game Boy Advance emulator within REG-Linux’s libretro ecosystem, supporting both libstdc++ build paths for ARM hosts.

## Build notes

- `Version`: a545aafaf4e654a488f4588f4f302d8413a58066
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
