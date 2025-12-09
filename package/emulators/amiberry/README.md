# Amiberry

Amiberry is the feature-complete Amiga emulator used by REG-Linux, wrapping SDL and audio libraries to reproduce classic hardware accurately on modern ARM64 hosts.

## Build notes

- `Version`: v7.1.1
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_MPG123`, `BR2_PACKAGE_LIBXML2`, `BR2_PACKAGE_LIBMPEG2`, `BR2_PACKAGE_FLAC`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBSERIALPORT`, `BR2_PACKAGE_LIBPORTMIDI`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBCAPSIMAGE`, `BR2_PACKAGE_LIBPCAP`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `000-amiberry-path.patch`
