# BR2_PACKAGE_PPSSPP

See Buildroot configs for details.

## Build notes

- ``Version``: v1.19.3
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_TTF, select BR2_PACKAGE_LIBZIP, select BR2_PACKAGE_LIBGLEW if BR2_PACKAGE_SYSTEM_TARGET_X86_ANY, select BR2_PACKAGE_LIBGLU  if BR2_PACKAGE_SYSTEM_TARGET_X86_ANY
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `psp.ppsspp.keys` into `/usr/share/evmapy` or equivalent; applies patches: 002-cmake-arm-conversion-fix.patch, 008-cmake-sdl2-ttf-fix.patch, 001-batocera-path.patch, 005-reduce_vulkan_checks.patch, 003-fullscreen_drm.patch, 004-statenameasromfilename.patch
