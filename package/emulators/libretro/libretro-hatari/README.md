# BR2_PACKAGE_LIBRETRO_HATARI

See Buildroot configs for details.

## Build notes

- ``Version``: 7008194d3f951a157997f67a820578f56f7feee0
- ``Config``: select BR2_PACKAGE_LIBCAPSIMAGE, select BR2_PACKAGE_ZLIB, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 003-ipf-uaecpu.patch, 002-floppy-ipf.patch, 004-fix-gcc14.patch, 001-pathconfig.patch, 000-makefile.patch
