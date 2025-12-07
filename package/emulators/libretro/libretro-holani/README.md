# BR2_PACKAGE_LIBRETRO_HOLANI

See Buildroot configs for details.

## Build notes

- ``Version``: 0.9.6-1
- ``Config``: select BR2_PACKAGE_HOST_RUSTC, depends on BR2_PACKAGE_HOST_RUSTC_TARGET_ARCH_SUPPORTS, depends on BR2_PACKAGE_LLVM, depends on BR2_PACKAGE_CLANG
- ``Build helper``: Custom build (see mk)
