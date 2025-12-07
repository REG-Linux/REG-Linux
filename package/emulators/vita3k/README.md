# BR2_PACKAGE_VITA3K

Experimental PlayStation Vita emulator https://github.com/vita3k/vita3k

## Build notes

- ``Version``: 3df27923b48c2ddf579b773814e05a315b00196f
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_IMAGE, select BR2_PACKAGE_SDL2_TTF, select BR2_PACKAGE_LIBGTK3, select BR2_PACKAGE_LIBOGG, select BR2_PACKAGE_LIBVORBIS, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_FILESYSTEM, select BR2_PACKAGE_BOOST_SYSTEM, select BR2_PACKAGE_PYTHON_RUAMEL_YAML, select BR2_PACKAGE_FMT, select BR2_PACKAGE_LIBCURL
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `psvita.vita3k.keys` into `/usr/share/evmapy` or equivalent; applies patches: 006-hack-ffmpeg-git-sha.patch, 005-fix-header.patch, 003-disable-nfd-portal.patch, 001-adjust-paths.patch, 004-lower-case-vita.patch
