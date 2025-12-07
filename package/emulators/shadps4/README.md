# BR2_PACKAGE_SHADPS4

Sony Playstation 4 emulator. https://github.com/shadps4-emu/shadPS4 https://shadps4.net/

## Build notes

- ``Version``: v.0.12.5
- ``Config``: select BR2_HOST_CMAKE_AT_LEAST_3_24, select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_PULSEAUDIO, select BR2_PACKAGE_OPENAL, select BR2_PACKAGE_OPENSSL, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBEDIT, select BR2_PACKAGE_UDEV, select BR2_PACKAGE_LIBEVDEV, select BR2_PACKAGE_JACK2, select BR2_PACKAGE_VULKAN_HEADERS, select BR2_PACKAGE_VULKAN_LOADER, select BR2_PACKAGE_VULKAN_VALIDATIONLAYERS, select BR2_PACKAGE_FFMPEG, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_FMT, select BR2_PACKAGE_GLSLANG, select BR2_PACKAGE_SDL3, depends on BR2_TOOLCHAIN_GCC_AT_LEAST_8
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `ps4.keys` into `/usr/share/evmapy` or equivalent
