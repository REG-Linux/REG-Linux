# BR2_PACKAGE_LIBRETRO_GEARBOY

Gearboy is a cross-platform Game Boy / Game Boy Color emulator written in C++ that runs on Windows, macOS, Linux, BSD and RetroArch.

## Build notes

- ``Version``: 3.7.4
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-makefile-additions.patch
