# Libretro mGBA

The `libretro-mgba` core delivers Game Boy Advance emulation to REG-Linux using libzip/libpng/zlib and the usual dual-libstdc++ builds.

## Build notes

- `Version`: 0.10.5
- `Dependencies`: `BR2_PACKAGE_LIBZIP`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_ZLIB`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `001-reduce-logs.patch`
