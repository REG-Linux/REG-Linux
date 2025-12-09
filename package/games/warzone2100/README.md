# Warzone 2100

Warzone 2100 supplies REG-Linux with the open-source 3D RTS (campaign/skirmish/multiplayer) built from the upstream CMake tree.

## Build notes

- `Version`: 4.6.1 release (Sept 2025).
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_LIBSODIUM`, `BR2_PACKAGE_SQLITE`, `BR2_PACKAGE_PROTOBUF`, `BR2_PACKAGE_LIBZIP`, `BR2_PACKAGE_PHYSFS`, `BR2_PACKAGE_OPENAL`, `BR2_PACKAGE_LIBTHEORA`, `BR2_PACKAGE_LIBCURL`, `BR2_INSTALL_LIBSTDCPP`.
- `Build helper`: CMake-based (`cmake-package`) with `WARZONE2100_SUPPORTS_IN_SOURCE_BUILD=NO`.
- `Extras`: installs `/usr/bin/warzone2100` and relies on the upstream asset shipping (no additional keys).
