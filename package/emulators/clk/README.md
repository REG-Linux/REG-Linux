# CLK

CLK (Clock Signal) is a multi-system emulator that targets classic home computers (BBC Micro, Acorn, etc.) and ships here for REG-Linux with SDL2-based I/O.

## Build notes

- `Version`: 2025-11-26
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ZLIB`, plus `BR2_PACKAGE_HAS_LIBGL` for optional OpenGL rendering
- `Build helper`: CMake-based (`cmake-package`)
