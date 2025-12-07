# BR2_PACKAGE_LIBRETRO_PICODRIVE

A libretro Megadrive SMS emulator core for ARM.

## Build notes

- ``Version``: v2.05
- ``Config``: select BR2_PACKAGE_LIBPNG, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP && !BR2_PACKAGE_LIBPNG
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-gcc14-fix.patch, 002-flto-auto.patch, 000-makefile.patch
