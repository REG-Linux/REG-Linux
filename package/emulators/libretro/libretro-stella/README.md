# BR2_PACKAGE_LIBRETRO_STELLA

A libretro Atari 2600 emulator core for ARM.

## Build notes

- ``Version``: 7.0
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-makefile-flto-auto.patch, 000-rpi_makefile.patch
