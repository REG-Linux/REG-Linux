# Libretro bsnes JG

The `libretro-bsnes-jg` core is REG-Linux’s libretro SNES backend with the "Ji" performance path, ensuring both standard and optimized builds work.

## Build notes

- `Version`: 6400024854702110c4019f5b0a7336dca7112fdb
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, `BR2_GCC_ENABLE_OPENMP`, and `!BR2_INSTALL_LIBSTDCPP` (build supports libstdc++ toggles)
- `Build helper`: Generic/Makefile (`generic-package`)
