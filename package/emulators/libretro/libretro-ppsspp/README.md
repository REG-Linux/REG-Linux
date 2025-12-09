# Libretro PPSSPP

The `libretro-ppsspp` core lets REG-Linux run PSP titles through libretro, keeping the standard libzip dependency and the distro’s path/cmake patches in place.

## Build notes

- `Version`: v1.19.3
- `Dependencies`: `BR2_PACKAGE_LIBZIP`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `001-custom-paths.patch`, `002-cmake-arm-conversion-fix.patch`, `000-batocera-path.patch`
