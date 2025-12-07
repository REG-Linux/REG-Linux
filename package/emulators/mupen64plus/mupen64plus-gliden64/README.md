# BR2_PACKAGE_MUPEN64PLUS_GLIDEN64

A new generation, open-source graphics plugin for N64 emulators.

## Build notes

- ``Version``: 55c436c706224eae6cd1395b88e083105b7d7834
- ``Config``: select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBPNG, select BR2_INSTALL_LIBSTDCPP, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_ALSA_LIB, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_SDL2 || !BR2_PACKAGE_ALSA_LIB
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 000-sdl2-fix.patch
