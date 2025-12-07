# yquake2 client

Main Yamagi Quake II engine.

## Build notes
- **Version:** tag `QUAKE2_8_60` from `yquake2/yquake2`.
- **Config:** depends on `libcurl` and either SDL2 or SDL3; selects GL renderers only when `BR2_PACKAGE_HAS_LIBGL` is enabled and an optional GLES3 renderer when `BR2_PACKAGE_HAS_GLES3` is available.
- **Build system:** CMake release build that installs the `quake2` and `q2ded` binaries, the software renderer, and both GL/GLES renderer shared libraries under `/usr/yquake2/`. Uses `cmake-package` and sets renderer flags explicitly for the target.
