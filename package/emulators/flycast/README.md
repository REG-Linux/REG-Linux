# BR2_PACKAGE_FLYCAST

Flycast is a multi-platform Sega Dreamcast, Naomi and Atomiswave emulator.

## Build notes

- ``Version``: v2.5
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBZIP, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_NOWIDE, select BR2_PACKAGE_LIBAO, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_LIBMINIUPNPC, select BR2_PACKAGE_ELFUTILS, select BR2_PACKAGE_GLSLANG		if BR2_PACKAGE_REGLINUX_VULKAN, depends on BR2_GCC_ENABLE_OPENMP
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `naomi2.flycast.keys, dreamcast.flycast.keys, naomi.flycast.keys, atomiswave.flycast.keys` into `/usr/share/evmapy` or equivalent; applies patches: 000-makefile-additions.patch
