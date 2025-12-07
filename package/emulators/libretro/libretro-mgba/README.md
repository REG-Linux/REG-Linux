# BR2_PACKAGE_LIBRETRO_MGBA

See Buildroot configs for details.

## Build notes

- ``Version``: 0.10.5
- ``Config``: select BR2_PACKAGE_LIBZIP, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_ZLIB, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 001-reduce-logs.patch
