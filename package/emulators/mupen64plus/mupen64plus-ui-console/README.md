# BR2_PACKAGE_MUPEN64PLUS_UI_CONSOLE

Console (command-line) front-end user interface for Mupen64Plus v2.0 project

## Build notes

- ``Version``: 2.6.0
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on BR2_PACKAGE_SDL2, depends on BR2_PACKAGE_ALSA_LIB, depends on BR2_PACKAGE_MUPEN64PLUS_CORE, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_SDL2 || !BR2_PACKAGE_ALSA_LIB
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-cheatfile.patch, 001-statenameasromfilename.patch
