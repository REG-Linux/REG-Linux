# Mupen64Plus UI console

The `mupen64plus-ui-console` package builds the CLI interface REG-Linux uses alongside the core and SDL/ALSA plugins.

## Build notes

- `Version`: 2.6.0
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_MUPEN64PLUS_CORE`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-cheatfile.patch` and `001-statenameasromfilename.patch`
