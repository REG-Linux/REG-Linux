# BR2_PACKAGE_LIBRETRO_MAME2003_PLUS

A libretro mame2003+ core for ARM.

## Build notes

- ``Version``: 62c7089644966f6ac5fc79fe03592603579a409d
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-enable-lto.patch, 000-makefile.patch
