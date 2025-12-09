# Hypseus-Singe

Hypseus-Singe is REG-Linux's fork of Daphne with Action Max (Singe) support, bundling SDL-based audio/visual helpers and dataset keys.

## Build notes

- `Version`: v2.11.6
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_SDL2_MIXER`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBOGG`, `BR2_PACKAGE_LIBVORBIS`, `BR2_PACKAGE_LIBMPEG2`, `BR2_PACKAGE_LIBZIP`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `daphne.hypseus-singe.keys` and `singe.hypseus-singe.keys` into `/usr/share/evmapy` (or equivalent) and applies `006-render-sinden-last.patch`, `001-git-fix.patch`, `002-mpeg2.patch`, `007-udev-event-no-read-if-no-sdlevent.patch`
