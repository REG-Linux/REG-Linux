# Libretro FB Alpha

The `libretro-fbalpha` core provides ARM-targeted arcade emulation within REG-Linux’s libretro stack.

## Build notes

- `Version`: 77167cea72e808384c136c8c163a6b4975ce7a84
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-fix-gcc14.patch`
