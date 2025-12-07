# BR2_PACKAGE_LIBRETRO_MAME2010

A libretro mame2010 core for ARM.

## Build notes

- ``Version``: c5b413b71e0a290c57fc351562cd47ba75bac105
- ``Config``: select BR2_PACKAGE_ZLIB, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-rpi_makefile.patch
