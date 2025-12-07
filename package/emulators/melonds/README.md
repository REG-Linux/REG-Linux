# BR2_PACKAGE_MELONDS

Ninteno DS emulator, sorta http://melonds.kuribo64.net/

## Build notes

- ``Version``: 1.1
- ``Config``: select BR2_PACKAGE_LIBARCHIVE, select BR2_PACKAGE_LIBEPOXY, select BR2_PACKAGE_LIBENET, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SLIRP, select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_ECM, select BR2_PACKAGE_FAAD2
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `nds.melonds.keys` into `/usr/share/evmapy` or equivalent; applies patches: 001-legacy-config.patch
