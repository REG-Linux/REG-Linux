# BR2_PACKAGE_DOLPHIN_TRIFORCE

See Buildroot configs for details.

## Build notes

- ``Version``: 5c456e8ff0da0235be2cf1d55ba7bb2115b0cae2
- ``Config``: select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_BLUEZ5_UTILS, select BR2_PACKAGE_FFMPEG, select BR2_PACKAGE_HIDAPI, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_LIBEVDEV, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBUSB, select BR2_PACKAGE_LZO, select BR2_PACKAGE_SPEEX, select BR2_PACKAGE_SPEEXDSP, select BR2_PACKAGE_XZ, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_MINIZIP_ZLIB, select BR2_PACKAGE_PUGIXML, select BR2_PACKAGE_SDL2, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_HAS_LIBGL
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `triforce.dolphin_triforce.keys` into `/usr/share/evmapy` or equivalent; applies patches: 006-fix-SetNextItemAllowOverlap.patch, 002-fix-package-name.patch, 007-fix-socket-linux.patch, 004-fix-fmt.patch, 001-fix-vulkanmemoryallocator.patch, 000-fix-install-cmake.patch, 005-fix-ImGuiButtonFlags_AllowOverlap.patch, 003-fix-cmake-lz4.patch
