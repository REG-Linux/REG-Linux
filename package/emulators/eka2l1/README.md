# BR2_PACKAGE_EKA2L1

Symbian OS / N-Gage emulator

## Build notes

- ``Version``: e67f84dc605ea30afc1ab6f4f43c0f855eec79a5
- ``Config``: select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_FFMPEG
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 001-gcc14-workaround.patch, 003-wip.patch, 002-force-qt6-cmake.patch
