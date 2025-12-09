# Mupen64Plus core

The `mupen64plus-core` module is the central engine of the Mupen64Plus project and ships the same plugin-based architecture to REG-Linux.

## Build notes

- `Version`: 2.6.0
- `Dependencies`: `BR2_PACKAGE_HOST_NASM`, `BR2_INSTALL_LIBSTDCPP`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_FREETYPE`, `BR2_PACKAGE_DEJAVU`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `005-fix-gcc14.patch`, `001-allow-96MB.patch`, `003-statenameasromfilename.patch`, `000-start-message.patch`, `002-mupeninifile.patch`, `004-statesasromname.patch`
