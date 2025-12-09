# Felix86

Felix86 brings x86_64 compatibility to REG-Linux's RISC-V builds, wrapping the OFFTKP emulator at https://github.com/OFFTKP/felix86 with Buildroot-friendly configuration.

## Build notes

- `Version`: 25.10
- `Dependencies`: `BR2_riscv && BR2_RISCV_64`, `BR2_PACKAGE_HAS_LIBGL`, `BR2_PACKAGE_VULKAN_HEADERS`, `BR2_PACKAGE_VULKAN_LOADER`
- `Build helper`: CMake-based (`cmake-package`)
