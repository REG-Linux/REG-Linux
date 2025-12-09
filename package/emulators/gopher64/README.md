# Gopher64

Gopher64 compiles the Rust-based N64 emulator for REG-Linux so that x86 and Wayland hosts can run Nintendo 64 content with Vulkan support.

## Build notes

- `Version`: v1.1.9
- `Dependencies`: `BR2_PACKAGE_HOST_RUSTC`, `BR2_PACKAGE_HOST_RUSTC_TARGET_ARCH_SUPPORTS`, `BR2_PACKAGE_CLANG`, `BR2_PACKAGE_WAYLAND`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_HAS_LIBGL`, `BR2_PACKAGE_XWAYLAND`, `BR2_PACKAGE_VULKAN_HEADERS`, `BR2_PACKAGE_VULKAN_LOADER`
- `Build helper`: Rust (`rust-package`)
- `Extras`: applies `001-lto-auto.patch`
