# BR2_PACKAGE_LIBRETRO_GEARSYSTEM

Gearsystem is a very accurate, cross-platform Sega Master System / Game Gear / SG-1000 / Othello Multivision emulator ritten in C++ that runs on Windows, macOS, Linux, BSD, iOS, Raspberry Pi and RetroArch.

## Build notes

- ``Version``: 3.8.5
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-makefile-additions.patch
