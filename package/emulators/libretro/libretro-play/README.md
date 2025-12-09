# Libretro Play!

The `libretro-play` core packages the PlayStation 2 emulator Play! (https://purei.org/) into REG-Linux with optional GL dependencies and the distro’s GLES/EGL tweaks.

## Build notes

- `Version`: 0.71
- `Dependencies`: `BR2_PACKAGE_LIBGLEW`, `BR2_PACKAGE_LIBGLU` when `BR2_PACKAGE_HAS_LIBGL`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `003-gcc13-fix.patch`, `002-aarch64-gles.patch`, `001-egl-no-x11.patch`
