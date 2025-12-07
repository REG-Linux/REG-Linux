# BR2_PACKAGE_DOLPHIN_EMU

See Buildroot configs for details.

## Build notes

- ``Version``: 2509
- ``Config``: select BR2_PACKAGE_LIBEVDEV, select BR2_PACKAGE_FFMPEG, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_XZ, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LZO, select BR2_PACKAGE_LIBUSB, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_BLUEZ5_UTILS, select BR2_PACKAGE_HIDAPI, select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL3, depends on BR2_x86_64 || BR2_aarch64, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_HAS_LIBGL
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `gamecube.dolphin.keys, wii.dolphin.keys` into `/usr/share/evmapy` or equivalent; applies patches: 011-savestate-with-romname.patch, 001-padorder.patch, 006-customtextures.patch, 008-bios-location.patch, 004-nicerlaunch.patch, 005-guns.patch, 007-disable-events-merging.patch, 1003-fix-libmali.patch, 003-hide-osd-msg.patch
