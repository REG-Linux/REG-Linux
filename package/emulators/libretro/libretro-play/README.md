# BR2_PACKAGE_LIBRETRO_PLAY

Play! - PlayStation2 Emulator https://purei.org/

## Build notes

- ``Version``: 0.71
- ``Config``: select BR2_PACKAGE_LIBGLEW	if BR2_PACKAGE_HAS_LIBGL, select BR2_PACKAGE_LIBGLU   if BR2_PACKAGE_HAS_LIBGL
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 003-gcc13-fix.patch, 002-aarch64-gles.patch, 001-egl-no-x11.patch
