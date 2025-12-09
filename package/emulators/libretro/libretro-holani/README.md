# Libretro Holani

The `libretro-holani` core merges the Rust-based SH/SCS emulation stack into REG-Linux, requiring Rust/LLVM tooling for build.

## Build notes

- `Version`: 0.9.6-1
- `Dependencies`: `BR2_PACKAGE_HOST_RUSTC`, `BR2_PACKAGE_HOST_RUSTC_TARGET_ARCH_SUPPORTS`, `BR2_PACKAGE_LLVM`, `BR2_PACKAGE_CLANG`
- `Build helper`: Custom build (see mk)
