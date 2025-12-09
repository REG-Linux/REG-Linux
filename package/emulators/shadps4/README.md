# shadPS4

`shadps4` packages the PS4 emulator for REG-Linux, bundling Vulkan/OpenAL/media tooling required upstream plus EVMapy keys.

## Build notes

- `Version`: v.0.12.5
- `Dependencies`: `BR2_HOST_CMAKE_AT_LEAST_3_24`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_PULSEAUDIO`, `BR2_PACKAGE_OPENAL`, `BR2_PACKAGE_OPENSSL`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBEDIT`, `BR2_PACKAGE_UDEV`, `BR2_PACKAGE_LIBEVDEV`, `BR2_PACKAGE_JACK2`, `BR2_PACKAGE_VULKAN_HEADERS`, `BR2_PACKAGE_VULKAN_LOADER`, `BR2_PACKAGE_VULKAN_VALIDATIONLAYERS`, `BR2_PACKAGE_FFMPEG`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_FMT`, `BR2_PACKAGE_GLSLANG`, `BR2_PACKAGE_SDL3`, `BR2_TOOLCHAIN_GCC_AT_LEAST_8`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `ps4.keys` into `/usr/share/evmapy`
