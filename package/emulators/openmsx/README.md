# BR2_PACKAGE_OPENMSX

A MSX emulator that aims for perfection.

## Build notes

- ``Version``: RELEASE_19_1
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_TTF, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBOGG, select BR2_PACKAGE_LIBVORBIS, select BR2_PACKAGE_LIBTHEORA, select BR2_PACKAGE_LIB, select BR2_PACKAGE_TCL, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_LIBGLEW	if BR2_PACKAGE_HAS_LIBGL, select BR2_PACKAGE_FREETYPE
- ``Build helper``: Autotools (autotools-package)
- ``Extras``: applies patches: 001-user-dir.patch, 002-filepool.patch, 003-fix-gcc14.patch
