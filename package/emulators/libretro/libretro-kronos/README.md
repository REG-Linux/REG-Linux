# BR2_PACKAGE_LIBRETRO_KRONOS

A libretro saturn emulator core.

## Build notes

- ``Version``: 2.7.0_official_release
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on BR2_PACKAGE_HAS_LIBGL || BR2_PACKAGE_HAS_LIBGLES, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 002-libretro-2.7.0-cumulative-patches.patch, 000-biospath.patch, 001-makefile.patch
