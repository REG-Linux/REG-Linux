# BR2_PACKAGE_LIBRETRO_MELONDS_DS

A remake of the libretro melonDS core that prioritizes standalone parity, reliability, and usability.

## Build notes

- ``Version``: e1391cc10a53b205963b7d1bd2b1f8d87d0d2cc7
- ``Config``: select BR2_PACKAGE_LIBPCAP, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: CMake-based (cmake-package)
