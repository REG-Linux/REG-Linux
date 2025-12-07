# BR2_PACKAGE_SNES9X

See Buildroot configs for details.

## Build notes

- ``Version``: 1.63
- ``Config``: select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_SDL2
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 001-make-x11-optional.patch, 002-use-x11-define.patch
