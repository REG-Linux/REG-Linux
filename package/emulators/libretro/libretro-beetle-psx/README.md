# BR2_PACKAGE_LIBRETRO_BEETLE_PSX

A libretro psx emulator core.

## Build notes

- ``Version``: b8dd9de6dba5fa0359c0a7df7f0b61a7fc503093
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-RPi5-tuning.patch, 000-makefile-no-cd.patch
