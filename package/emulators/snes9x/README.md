# Snes9x

The standalone `snes9x` build keeps the Qt6 + SDL2 frontend ready for REG-Linux with optional X11 patches.

## Build notes

- `Version`: 1.63
- `Dependencies`: `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_SDL2`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `001-make-x11-optional.patch`, `002-use-x11-define.patch`
