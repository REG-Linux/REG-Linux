# BR2_PACKAGE_LIBRETRO_DOSBOX_PURE

A libretro DOS emulator core.

## Build notes

- ``Version``: 1.0-preview4
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-rpi_makefile.patch
