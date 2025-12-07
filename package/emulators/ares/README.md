# BR2_PACKAGE_ARES

ares is a cross-platform, open source, multi-system emulator, focusing on accuracy and preservation. https://ares-emu.net/

## Build notes

- ``Version``: v146
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_PANGO, select BR2_PACKAGE_CAIRO, select BR2_PACKAGE_LIBGTK3, select BR2_PACKAGE_LIBRASHADER, depends on BR2_PACKAGE_HAS_LIBGL && BR2_ARCH_IS_64, depends on BR2_PACKAGE_XORG7 && BR2_PACKAGE_REGLINUX_XWAYLAND
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 000-cmake-sourcery-only.patch, 001-cmake-fixes.patch
