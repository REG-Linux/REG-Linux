# Libretro Panda3DS

The `libretro-panda3ds` core ports the Panda3DS Nintendo 3DS emulator to REG-Linux with red-panda branding and Vulkan-ready tooling.

## Build notes

- `Version`: v0.9-fix
- `Dependencies`: `BR2_PACKAGE_SDL2`, and when `BR2_PACKAGE_REGLINUX_VULKAN` is enabled `BR2_PACKAGE_GLSLANG` and `BR2_PACKAGE_HOST_GLSLANG`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `001-cmake-fix-glslang.patch`, `003-fix-renderer-vk.patch`, `002-glad-no-glx.patch`
