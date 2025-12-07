# BR2_PACKAGE_LIBRETRO_BLASTEM

A libretro SEGA 16 bits emulator core for x86.

## Build notes

- ``Version``: 842de15d6b59
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-force-newcore-noarch.patch, 002-fix-cpu-dsl.patch, 003-fix-vdp-nothread.patch, 001-fix-gcc14-error.patch
