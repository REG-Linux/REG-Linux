# BR2_PACKAGE_LIBRETRO_FCEUMM

A libretro NES emulator core for ARM.

## Build notes

- ``Version``: 5cd4a43e16a7f3cd35628d481c347a0a98cfdfa2
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-RPi5-tuning.patch, 002-enable-lto.patch
