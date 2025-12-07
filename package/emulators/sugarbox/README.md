# BR2_PACKAGE_SUGARBOX

See Buildroot configs for details.

## Build notes

- ``Version``: v2.0.4
- ``Config``: depends on BR2_PACKAGE_REGLINUX_HAS_QT6
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 001-qt6.patch, 002-c++1z.patch, 000-fix-install-dirs.patch, 003-disable-cpack.patch, 004-fix-gcc14.patch
