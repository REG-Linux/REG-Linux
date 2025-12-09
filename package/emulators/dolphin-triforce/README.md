# Dolphin Triforce

Dolphin Triforce targets the arcade-focused Nintendo "Triforce" platform (Mario Kart, F-Zero), so the REG-Linux build bundles the emulator with the extra key materials and Qt/SDL helpers needed for that loader.

## Build notes

- `Version`: 5c456e8ff0da0235be2cf1d55ba7bb2115b0cae2
- `Dependencies`: `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_BLUEZ5_UTILS`, `BR2_PACKAGE_FFMPEG`, `BR2_PACKAGE_HIDAPI`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_LIBEVDEV`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBUSB`, `BR2_PACKAGE_LZO`, `BR2_PACKAGE_SPEEX`, `BR2_PACKAGE_SPEEXDSP`, `BR2_PACKAGE_XZ`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_MINIZIP_ZLIB`, `BR2_PACKAGE_PUGIXML`, `BR2_PACKAGE_SDL2`, `!BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_HAS_LIBGL`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `triforce.dolphin_triforce.keys` into `/usr/share/evmapy` (or equivalent) and applies REG-Linux patches (`006-fix-SetNextItemAllowOverlap.patch`, `002-fix-package-name.patch`, `007-fix-socket-linux.patch`, `004-fix-fmt.patch`, `001-fix-vulkanmemoryallocator.patch`, `000-fix-install-cmake.patch`, `005-fix-ImGuiButtonFlags_AllowOverlap.patch`, `003-fix-cmake-lz4.patch`)
