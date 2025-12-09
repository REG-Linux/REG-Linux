# Libretro melonDS DS

The `libretro-melonds-ds` core recreates melonDS inside REG-Linux with a focus on parity and reliability while reusing the standalone experience.

## Build notes

- `Version`: e1391cc10a53b205963b7d1bd2b1f8d87d0d2cc7
- `Dependencies`: `BR2_PACKAGE_LIBPCAP`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: CMake-based (`cmake-package`)
