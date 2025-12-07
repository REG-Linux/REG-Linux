# BR2_PACKAGE_HYPSEUS_SINGE

Hypseus is a fork of Daphne with support for Action Max (Singe) games. https://github.com/DirtBagXon/hypseus-singe

## Build notes

- ``Version``: v2.11.6
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_IMAGE, select BR2_PACKAGE_SDL2_MIXER, select BR2_PACKAGE_SDL2_TTF, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBOGG, select BR2_PACKAGE_LIBVORBIS, select BR2_PACKAGE_LIBMPEG2, select BR2_PACKAGE_LIBZIP
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `daphne.hypseus-singe.keys, singe.hypseus-singe.keys` into `/usr/share/evmapy` or equivalent; applies patches: 006-render-sinden-last.patch, 001-git-fix.patch, 002-mpeg2.patch, 007-udev-event-no-read-if-no-sdlevent.patch
