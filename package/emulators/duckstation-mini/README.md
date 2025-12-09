# DuckStation Mini

DuckStation Mini targets ARM/AArch64 devices with a fullscreen Dear ImGui interface so PS1 titles run smoothly on REG-Linux consoles.

## Build notes

- `Version`: v0.1-9669
- `Dependencies`: `BR2_PACKAGE_GMP`, either `BR2_arm` or `BR2_aarch64`, and either `BR2_PACKAGE_HAS_GLES3` or `BR2_PACKAGE_REGLINUX_VULKAN` for graphics
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `psx.duckstation.keys` into `/usr/share/evmapy` (or the equivalent key directory)
