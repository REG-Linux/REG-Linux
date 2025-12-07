# BR2_PACKAGE_IZAPPLE2

Portable emulator of an Apple II+ or //e. Written in Go.

## Build notes

- ``Version``: v2.2
- ``Config``: select BR2_PACKAGE_HOST_GO, depends on BR2_PACKAGE_HOST_GO_TARGET_ARCH_SUPPORTS, depends on BR2_PACKAGE_HOST_GO_TARGET_CGO_LINKING_SUPPORTS, depends on BR2_TOOLCHAIN_HAS_THREADS, depends on BR2_PACKAGE_HOST_GO_TARGET_ARCH_SUPPORTS
- ``Build helper``: Go (golang-package)
