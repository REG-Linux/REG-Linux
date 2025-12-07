# BR2_PACKAGE_MUPEN64PLUS_CORE

Core module of the Mupen64Plus project

## Build notes

- ``Version``: 2.6.0
- ``Config``: select BR2_PACKAGE_HOST_NASM, depends on BR2_INSTALL_LIBSTDCPP, depends on BR2_PACKAGE_SDL2, depends on BR2_PACKAGE_ALSA_LIB, depends on BR2_PACKAGE_FREETYPE, depends on BR2_PACKAGE_DEJAVU, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_SDL2 || !BR2_PACKAGE_ALSA_LIB
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 005-fix-gcc14.patch, 001-allow-96MB.patch, 003-statenameasromfilename.patch, 000-start-message.patch, 002-mupeninifile.patch, 004-statesasromname.patch
