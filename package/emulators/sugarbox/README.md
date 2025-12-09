# Sugarbox

Sugarbox is REG-Linux’s Qt6-native shell for loading arcade/downscaled platforms, built with CMake to align with the distro’s Qt policies.

## Build notes

- `Version`: v2.0.4
- `Dependencies`: `BR2_PACKAGE_REGLINUX_HAS_QT6`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `001-qt6.patch`, `002-c++1z.patch`, `000-fix-install-dirs.patch`, `003-disable-cpack.patch`, `004-fix-gcc14.patch`
