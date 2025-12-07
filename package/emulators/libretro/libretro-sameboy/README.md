# BR2_PACKAGE_LIBRETRO_SAMEBOY

DMG/CGB GameBoy emulator for libretro

## Build notes

- ``Version``: v1.0.2
- ``Config``: select BR2_PACKAGE_RGBDS, select BR2_PACKAGE_XXD, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-makefile_hexdump.patch
