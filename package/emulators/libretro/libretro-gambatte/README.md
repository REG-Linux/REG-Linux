# BR2_PACKAGE_LIBRETRO_GAMBATTE

A libretro GAMEBOY emulator core for ARM.

## Build notes

- ``Version``: 5707c1806fbca784c22550db1fa2ce7ed646df09
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-RPi5-tuning.patch
