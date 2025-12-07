# BR2_PACKAGE_EDEN

Eden: Nintendo Switch Emulator

## Build notes

- ``Version``: v0.0.4-rc3
- ``Config``: select BR2_PACKAGE_JSON_FOR_MODERN_CPP, select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_FMT, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_CONTEXT, select BR2_PACKAGE_BOOST_FILESYSTEM, select BR2_PACKAGE_ZSTD, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBZIP, select BR2_PACKAGE_LIBUSB, select BR2_PACKAGE_LZ4, select BR2_PACKAGE_CATCH2, select BR2_PACKAGE_OPUS, select BR2_PACKAGE_ENET, select BR2_PACKAGE_GAMEMODE, select BR2_PACKAGE_LIBVA, select BR2_PACKAGE_REGLINUX_XWAYLAND, select BR2_PACKAGE_FFMPEG, select BR2_PACKAGE_HOST_YASM		if BR2_x86_64, select BR2_PACKAGE_MBEDTLS, depends on BR2_x86_64 || BR2_aarch64
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `switch.eden.keys` into `/usr/share/evmapy` or equivalent; applies patches: 001-fix-sse2neon.patch, 004-format_custom.patch, 002-adjust-paths.patch, 003-external-nx-tzdb-prebuilt.patch
