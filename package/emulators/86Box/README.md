# 86Box

86Box brings a configurable x86 PC environment to REG-Linux, letting users run classic DOS/Windows software with high accuracy and optional Vulkan rendering. The upstream project lives at https://86box.net/, but REG-Linux keeps its own build tweaks.

## Build notes

- `Version`: v5.2
- `Dependencies`: `BR2_PACKAGE_RTMIDI`, `BR2_PACKAGE_LIBSNDFILE`, `BR2_PACKAGE_SLIRP`, `BR2_PACKAGE_OPENAL`, `BR2_PACKAGE_SDL2`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `002-reglinux-fix-build.patch` and `001-reglinux-vulkan-optional.patch` during the recipe
