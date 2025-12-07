# BR2_PACKAGE_LIBRETRO_BEETLE_PCE_FAST

A libretro PCE-FAST emulator core for ARM. http://www.libretro.com

## Build notes

- ``Version``: be659edd93cd84e01e13ab3c44a6354662d37e4e
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-RPi5-tuning.patch, 000-makefile-no-cd.patch
