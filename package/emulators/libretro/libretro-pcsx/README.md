# BR2_PACKAGE_LIBRETRO_PCSX

A libretro psx emulator core for ARM.

## Build notes

- ``Version``: 228c14e10e9a8fae0ead8adf30daad2cdd8655b9
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-makefile-rk3326-64.patch, 001-RPi5-tuning.patch
