# BR2_PACKAGE_SIMCOUPE

See Buildroot configs for details.

## Build notes

- ``Version``: v1.2.15
- ``Config``: select BR2_PACKAGE_SDL2, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `samcoupe.keys` into `/usr/share/evmapy` or equivalent; applies patches: 0002-add-pad-configuration-options.patch, 0003-use-pad-configuration.patch, 0001-aarch64-little-endian.patch
