# BR2_PACKAGE_LIBRETRO_GEARGRAFX

Geargrafx is an accurate cross-platform

## Build notes

- ``Version``: 1.6.4
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-fix-libchdr-musl.patch, 000-makefile-additions.patch
