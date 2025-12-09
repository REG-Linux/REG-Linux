# Hurrican

The `Hurrican` SDL2 fork delivers a 2D shooter/platformer with GLES2 rendering and the distro’s audio/SDL helpers.

## Build notes

- `Version`: `16205675479d49f...` (Nov 2025) commit from `HurricanGame/Hurrican`.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_MIXER`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_LIBEPOXY`, `BR2_PACKAGE_LIBOPENMPT`, `BR2_INSTALL_LIBSTDCPP`.
- `Build helper`: CMake-based (`cmake-package`) with `-DRENDERER=GLES2` and the `001-paths.patch` fix.
- `Extras`: installs `/usr/bin/hurrican`, drops `hurrican.keys` into `/usr/share/evmapy`, and lays down `/usr/share/hurrican` data directories.
