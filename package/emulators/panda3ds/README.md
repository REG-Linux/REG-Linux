# BR2_PACKAGE_PANDA3DS

Panda3DS is an HLE, red-panda-themed Nintendo 3DS emulator written in C++ which started out as a fun project out of curiosity, but evolved into something that can sort of play games! https://github.com/wheremyfoodat/Panda3DS

## Build notes

- ``Version``: v0.9-fix
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_GLSLANG		if BR2_PACKAGE_REGLINUX_VULKAN, select BR2_PACKAGE_HOST_GLSLANG	if BR2_PACKAGE_REGLINUX_VULKAN
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 001-cmake-fix-glslang.patch, 003-fix-renderer-vk.patch, 002-glad-no-glx.patch
