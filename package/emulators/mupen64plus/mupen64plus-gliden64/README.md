# Mupen64Plus GlideN64

The `mupen64plus-gliden64` plugin delivers the next-gen OpenGL graphics stack for REG-Linux’s N64 builds, hooking into SDL2/ALSA and libpng/zlib.

## Build notes

- `Version`: 55c436c706224eae6cd1395b88e083105b7d7834
- `Dependencies`: `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBPNG`, `BR2_INSTALL_LIBSTDCPP`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ALSA_LIB`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `000-sdl2-fix.patch`
