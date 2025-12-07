# BR2_PACKAGE_HATARI

An Atari ST/STe/TT/Falcon emulator

## Build notes

- ``Version``: v2.6.1
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBCAPSIMAGE
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `atarist.hatari.keys` into `/usr/share/evmapy` or equivalent; applies patches: 004-no-testing-no-manpages.patch, 001-tospath.patch, 003-enforce-lto.patch, 002-configpath.patch
