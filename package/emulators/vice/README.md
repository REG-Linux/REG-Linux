# VICE

The standalone `vice` port builds every Commodore 8-bit binary (x64, x128, xvic, xplus4, xpet, xcbm2, x64dtv, x64sc, xscpu64) using SDL2/SDL2_image and the usual audio libs for REG-Linux.

## Build notes

- `Version`: 3.9
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_PNG`, `BR2_PACKAGE_JPEG`, `BR2_PACKAGE_GIFLIB`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LAME`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_LIBVORBIS`, `BR2_PACKAGE_MPG123`, `BR2_PACKAGE_FLAC`, `BR2_PACKAGE_HOST_XA`, `BR2_PACKAGE_HOST_DOS2UNIX`, `BR2_PACKAGE_VICE`
- `Build helper`: Autotools (`autotools-package`)
- `Extras`: copies `c64.vice.keys` and `c128.vice.keys` into `/usr/share/evmapy` and applies `000-fix-segfault.patch`
