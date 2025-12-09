# Libretro Beetle PCE Fast

The `libretro-beetle-pce-fast` core provides the faster TurboGrafx engine for REG-Linux, including Raspberry Pi tuning and the CD-less Makefile variant.

## Build notes

- `Version`: be659edd93cd84e01e13ab3c44a6354662d37e4e
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-RPi5-tuning.patch` and `000-makefile-no-cd.patch`
