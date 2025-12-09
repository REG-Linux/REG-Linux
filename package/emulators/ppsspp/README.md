# PPSSPP

`ppsspp` delivers the open-source PSP emulator to REG-Linux with SDL2/GL helpers and the usual EVMapy key handling.

## Build notes

- `Version`: v1.19.3
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_LIBZIP`, `BR2_PACKAGE_LIBGLEW`, `BR2_PACKAGE_LIBGLU` (for `BR2_PACKAGE_SYSTEM_TARGET_X86_ANY`)
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `psp.ppsspp.keys` into `/usr/share/evmapy` and applies `002-cmake-arm-conversion-fix.patch`, `008-cmake-sdl2-ttf-fix.patch`, `001-batocera-path.patch`, `005-reduce_vulkan_checks.patch`, `003-fullscreen_dRM.patch`, `004-statenameasromfilename.patch`
