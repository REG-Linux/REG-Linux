# EKA2L1

EKA2L1 emulates Symbian OS and classic N-Gage software for REG-Linux, leveraging Qt6 and multimedia helpers for compatibility.

## Build notes

- `Version`: e67f84dc605ea30afc1ab6f4f43c0f855eec79a5
- `Dependencies`: `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_FFMPEG`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies REG-Linux patches (`001-gcc14-workaround.patch`, `003-wip.patch`, `002-force-qt6-cmake.patch`)
