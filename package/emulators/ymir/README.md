# BR2_PACKAGE_YMIR

A work-in-progress Sega Saturn emulator. https://github.com/StrikerX3/Ymir

## Build notes

- ``Version``: v0.2.0
- ``Config``: select BR2_PACKAGE_CEREAL, select BR2_PACKAGE_CXXOPTS, select BR2_PACKAGE_DATE, select BR2_PACKAGE_FMT, select BR2_PACKAGE_JSON_FOR_MODERN_CPP, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_LIBXKBCOMMON, select BR2_PACKAGE_NGHTTP3, select BR2_PACKAGE_RTMIDI, select BR2_PACKAGE_SDL3, select BR2_PACKAGE_SEMVER, select BR2_PACKAGE_STB, select BR2_PACKAGE_TOMLPLUSPLUS, select BR2_PACKAGE_WAYLAND, select BR2_PACKAGE_WAYLAND_PROTOCOLS, depends on BR2_PACKAGE_CLANG, depends on BR2_PACKAGE_HAS_LIBEGL
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 005-FROM-GIT-fix-date.patch, 003-libcurl-dynamic-cmake.patch, 001-use-system-sdl3.patch, 004-about-window-no-ngtcp2.patch, 002-no-stb-cmake.patch
