# IzApple2

IzApple2 ports the Go-based Apple II+///e emulator to REG-Linux so classic 8-bit software can run alongside the distro’s UI.

## Build notes

- `Version`: v2.2
- `Dependencies`: `BR2_PACKAGE_HOST_GO`, `BR2_PACKAGE_HOST_GO_TARGET_ARCH_SUPPORTS`, `BR2_PACKAGE_HOST_GO_TARGET_CGO_LINKING_SUPPORTS`, `BR2_TOOLCHAIN_HAS_THREADS`
- `Build helper`: Go (`golang-package`)
