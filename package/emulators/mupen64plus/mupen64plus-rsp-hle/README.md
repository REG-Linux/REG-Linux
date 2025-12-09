# Mupen64Plus RSP HLE

The `mupen64plus-rsp-hle` plugin provides the high-level RSP implementation REG-Linux needs for modern N64 titles.

## Build notes

- `Version`: 2.6.0
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ALSA_LIB`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-aarch64.patch`
