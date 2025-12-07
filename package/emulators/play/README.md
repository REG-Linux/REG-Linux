# BR2_PACKAGE_PLAY

Play! is a PlayStation2 emulator. https://purei.org/

## Build notes

- ``Version``: 0.71
- ``Config``: select BR2_PACKAGE_PCRE2, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_LIBCURL_OPENSSL, select BR2_PACKAGE_LIBGLEW		               if BR2_PACKAGE_REGLINUX_XWAYLAND, select BR2_PACKAGE_LIBGLU		               if BR2_PACKAGE_REGLINUX_XWAYLAND, select BR2_PACKAGE_OPENAL, select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_SQLITE, select BR2_PACKAGE_ECM
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `ps2.play.keys, namco2x6.keys` into `/usr/share/evmapy` or equivalent; applies patches: 002-fix-arcadepath.patch, 003-gcc13-fix.patch, 001-fpic.patch, 004-fix-zlib-ng.patch
