# BR2_PACKAGE_LIBRETRO_NESTOPIA

A libretro NES & FDS emulator core for ARM.

## Build notes

- ``Version``: 3ac52e67c4a7fa696ee37e48bbcec93611277288
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-rpi5-tuning.patch
