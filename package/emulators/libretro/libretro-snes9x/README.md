# BR2_PACKAGE_LIBRETRO_SNES9X

Snes9x - Portable Super Nintendo Entertainment System (TM) emulator http://www.snes9x.com

## Build notes

- ``Version``: 49f484569ff2aec7ff08e7598a97d6c9e6eae72d
- ``Config``: select BR2_PACKAGE_ZLIB, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 002-enable-flto-auto.patch, 001-RPi5-tuning.patch, 003-enable-zip-msu1.patch, 004-hack-zip-msu1-fixup.patch
