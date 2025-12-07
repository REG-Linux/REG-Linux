# BR2_PACKAGE_RPCS3

RPCS3 is a multi-platform open-source Sony PlayStation 3 emulator. https://rpcs3.net/

## Build notes

- ``Version``: v0.0.38
- ``Config``: select BR2_HOST_CMAKE_AT_LEAST_3_24, select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_LLVM, select BR2_PACKAGE_FFMPEG_SWSCALE, select BR2_PACKAGE_LIBEVDEV, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBGLEW, select BR2_PACKAGE_LIBGLU, select BR2_PACKAGE_LIBUSB, select BR2_PACKAGE_LIBXML2, select BR2_PACKAGE_MESA3D, select BR2_PACKAGE_NCURSES, select BR2_PACKAGE_OPENAL, select BR2_PACKAGE_PUGIXML, select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_RTMIDI, select BR2_PACKAGE_RTMPDUMP, select BR2_PACKAGE_SDL3, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_ZSTD, depends on BR2_TOOLCHAIN_GCC_AT_LEAST_8
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `evmapy.keys` into `/usr/share/evmapy` or equivalent; applies patches: 013-gun-support.patch, 010-padsevdev.patch, 014-gun-mapping.patch, 012-savestate-location.patch, 006-no-firmware-confirmation.patch, 004-fix-iconv.patch, 007-fix-screenshot-directory.patch, 001-fix-libusb.patch
