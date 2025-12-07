# BR2_PACKAGE_LIBRETRO_FLYCAST

A libretro dreamcast emulator core.

## Build notes

- ``Version``: $(FLYCAST_VERSION)
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on BR2_GCC_ENABLE_OPENMP, depends on (BR2_PACKAGE_HAS_LIBGLES || BR2_PACKAGE_HAS_LIBGL), depends on !BR2_INSTALL_LIBSTDCPP || \
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 000-makefile-additions.patch
