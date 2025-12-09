# Ymir

Ymir is the Sega Saturn effort upstream that REG-Linux builds with modern C++ tooling, SDL3/WAYLAND helpers, and optional EGL support.

## Build notes

- `Version`: v0.2.0
- `Dependencies`: `BR2_PACKAGE_CEREAL`, `BR2_PACKAGE_CXXOPTS`, `BR2_PACKAGE_DATE`, `BR2_PACKAGE_FMT`, `BR2_PACKAGE_JSON_FOR_MODERN_CPP`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_LIBXKBCOMMON`, `BR2_PACKAGE_NGHTTP3`, `BR2_PACKAGE_RTMIDI`, `BR2_PACKAGE_SDL3`, `BR2_PACKAGE_SEMVER`, `BR2_PACKAGE_STB`, `BR2_PACKAGE_TOMLPLUSPLUS`, `BR2_PACKAGE_WAYLAND`, `BR2_PACKAGE_WAYLAND_PROTOCOLS`, `BR2_PACKAGE_CLANG`, `BR2_PACKAGE_HAS_LIBEGL`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `005-FROM-GIT-fix-date.patch`, `003-libcurl-dynamic-cmake.patch`, `001-use-system-sdl3.patch`, `004-about-window-no-ngtcp2.patch`, `002-no-stb-cmake.patch`
