# Dolphin Emulator

Dolphin Emulator brings GameCube and Wii compatibility into REG-Linux, bundling the latest upstream changes plus REG-Linux-specific patches so the Qt/SGL frontend behaves consistently on Linux targets.

## Build notes

- `Version`: 2509
- `Dependencies`: `BR2_PACKAGE_LIBEVDEV`, `BR2_PACKAGE_FFMPEG`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_XZ`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LZO`, `BR2_PACKAGE_LIBUSB`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_BLUEZ5_UTILS`, `BR2_PACKAGE_HIDAPI`, `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL3`, `BR2_x86_64 || BR2_aarch64`, `!BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_HAS_LIBGL`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: installs `gamecube.dolphin.keys` and `wii.dolphin.keys` into `/usr/share/evmapy` (or equivalent) and applies REG-Linux patches (`011-savestate-with-romname.patch`, `001-padorder.patch`, `006-customtextures.patch`, `008-bios-location.patch`, `004-nicerlaunch.patch`, `005-guns.patch`, `007-disable-events-merging.patch`, `1003-fix-libmali.patch`, `003-hide-osd-msg.patch`)
