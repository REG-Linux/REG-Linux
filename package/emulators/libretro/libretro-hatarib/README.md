# BR2_PACKAGE_LIBRETRO_HATARIB

See Buildroot configs for details.

## Build notes

- ``Version``: 162d2ed3ee40d8ea394607e7f886a084b660ad5f
- ``Config``: select BR2_PACKAGE_LIBCAPSIMAGE, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_ZLIB, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 005-cmakeflags.patch, 002-no-bundled-sdl-zlib.patch, 004-remove-shorthash.patch, 003-hatari-cmake-crosscompiling.patch, 001-fix-soname.patch
