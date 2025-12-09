# Mupen64Plus video Glide64mk2

The `mupen64plus-video-glide64mk2` plugin keeps Gonetz’s Anniversary Glide64 renderer working within REG-Linux’s SDL/ALSA-backed Mupen64Plus builds.

## Build notes

- `Version`: 2.6.0
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_SYSTEM`, `BR2_PACKAGE_BOOST_FILESYSTEM`, `BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-hide-framebuffer-message.patch`
