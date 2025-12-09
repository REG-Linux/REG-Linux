# Ares

Ares is REG-Linux's modern multi-system emulator, prioritizing accurate hardware timing and compatibility for a wide range of consoles. More at https://ares-emu.net/.

## Build notes

- `Version`: v146
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_PANGO`, `BR2_PACKAGE_CAIRO`, `BR2_PACKAGE_LIBGTK3`, `BR2_PACKAGE_LIBRASHADER`, plus `BR2_PACKAGE_HAS_LIBGL && BR2_ARCH_IS_64` and `BR2_PACKAGE_XORG7 && BR2_PACKAGE_REGLINUX_XWAYLAND`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `000-cmake-sourcery-only.patch` and `001-cmake-fixes.patch`
