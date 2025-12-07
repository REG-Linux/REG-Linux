# BR2_PACKAGE_LIBRETRO_PUAE

A libretro AMIGA emulator core for ARM.

## Build notes

- ``Version``: f1c248602abb58e7c570feec3f59f4677407b252
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 002-isoc99math.patch, 001-capsimg-path.patch, 003-fix-gcc14.patch, 000-makefile.patch
