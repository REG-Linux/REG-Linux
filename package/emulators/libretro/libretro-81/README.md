# BR2_PACKAGE_LIBRETRO_81

A libretro EightyOne ZX81 emulator core.

## Build notes

- ``Version``: ffc99f27f092addc9ddd34dd0e3a3d4d1c053cbf
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `zx81.keys` into `/usr/share/evmapy` or equivalent; applies patches: 001-slowerkeyboard.patch, 000-rpi_makefile.patch
