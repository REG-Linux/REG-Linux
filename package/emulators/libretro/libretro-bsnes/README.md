# Libretro bsnes

The `libretro-bsnes` core provides REG-Linux with the standard bsnes SNES emulation path and the same OpenMP-aware build options.

## Build notes

- `Version`: f83ce97f0f0396846a3c9ed976259c67312e948e
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, `BR2_GCC_ENABLE_OPENMP`, and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
