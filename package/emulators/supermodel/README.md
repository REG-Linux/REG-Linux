# BR2_PACKAGE_SUPERMODEL

Supermodel is a SEGA Model 3 emulator that uses the SDL-Library. http://www.supermodel3.com source: https://github.com/trzy/Supermodel

## Build notes

- ``Version``: v0.3a-git-4e5905f
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_NET, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBGLEW, select BR2_PACKAGE_LIBGLU, select BR2_PACKAGE_LIBZIP, depends on BR2_INSTALL_LIBSTDCPP, depends on BR2_PACKAGE_XORG7 # libglew, depends on BR2_PACKAGE_HAS_LIBGL # libglew, depends on BR2_PACKAGE_XORG7, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_HAS_LIBGL
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `model3.supermodel.keys` into `/usr/share/evmapy` or equivalent; applies patches: 001-folder-directory.patch, 003-cross-compile.patch, 005-evdev-for-guns.patch, 004-game-settings.patch, 002-updatetemplate.patch
