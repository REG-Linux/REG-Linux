# BR2_PACKAGE_LIBRETRO_PPSSPP

A libretro PSP core http://www.libretro.com

## Build notes

- ``Version``: v1.19.3
- ``Config``: select BR2_PACKAGE_LIBZIP, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 001-custom-paths.patch, 002-cmake-arm-conversion-fix.patch, 000-batocera-path.patch
