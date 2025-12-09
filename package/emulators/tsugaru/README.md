# Tsugaru

Tsugaru emulates the FM Towns computer for REG-Linux, packaging the Qt/CMake frontend with GLU support.

## Build notes

- `Version`: v20250513
- `Dependencies`: `BR2_PACKAGE_LIBGLU`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `fmtowns.keys` into `/usr/share/evmapy` and applies `001-cmake-fixes.patch`
