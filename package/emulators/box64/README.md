# Box64

Box64 lets REG-Linux run x86_64 binaries on aarch64 or RISC-V hosts, leveraging upstream work from https://github.com/ptitseb/box64.

## Build notes

- `Version`: v0.3.8
- `Dependencies`: `BR2_aarch64 || BR2_RISCV_64`, `BR2_PACKAGE_HOST_PYTHON3`
- `Build helper`: CMake-based (`cmake-package`)
