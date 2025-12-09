# Flycast

Flycast emulates Sega Dreamcast, Naomi, and Atomiswave hardware with REG-Linux-specific keys and Vulkan-enabled rendering paths.

## Build notes

- `Version`: v2.5
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBZIP`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_NOWIDE`, `BR2_PACKAGE_LIBAO`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_LIBMINIUPNPC`, `BR2_PACKAGE_ELFUTILS`, `BR2_PACKAGE_GLSLANG` (when `BR2_PACKAGE_REGLINUX_VULKAN`), `BR2_GCC_ENABLE_OPENMP`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: installs `naomi2.flycast.keys`, `dreamcast.flycast.keys`, `naomi.flycast.keys`, and `atomiswave.flycast.keys` into `/usr/share/evmapy` (or the equivalent) and applies `000-makefile-additions.patch`
