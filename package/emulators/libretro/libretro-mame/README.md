# BR2_PACKAGE_LIBRETRO_MAME

A libretro mame core for Mame.

## Build notes

- ``Version``: lrmame0280
- ``Config``: select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_HAS_LIBRETRO_MAME, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 004-batocera-ini.patch, 005-flto-auto-genie.patch, 007-libretro-fix-joystick-4-way-option.patch, 003-nopch.patch, 006-libretro-mame-0277-buildfix.patch, 010-add-prepare-script.patch, 001-mame-cross-compilation.patch
