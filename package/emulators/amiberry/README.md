# BR2_PACKAGE_AMIBERRY

See Buildroot configs for details.

## Build notes

- ``Version``: v7.1.1
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_IMAGE, select BR2_PACKAGE_SDL2_TTF, select BR2_PACKAGE_MPG123, select BR2_PACKAGE_LIBXML2, select BR2_PACKAGE_LIBMPEG2, select BR2_PACKAGE_FLAC, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBSERIALPORT, select BR2_PACKAGE_LIBPORTMIDI, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBCAPSIMAGE, select BR2_PACKAGE_LIBPCAP
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 000-amiberry-path.patch
