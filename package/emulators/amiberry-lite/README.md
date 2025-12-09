# Amiberry Lite

Amiberry Lite is a streamlined Amiga emulator tuned for ARM platforms; REG-Linux keeps the Buildroot recipe lean while preserving the SDL-based UI.

## Build notes

- `Version`: v5.9.1
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_MPG123`, `BR2_PACKAGE_LIBXML2`, `BR2_PACKAGE_LIBMPEG2`, `BR2_PACKAGE_FLAC`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBSERIALPORT`, `BR2_PACKAGE_LIBPORTMIDI`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBCAPSIMAGE`, `BR2_PACKAGE_LIBENET`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `000-amiberry-path.patch` and `002-fix-musl.patch`
