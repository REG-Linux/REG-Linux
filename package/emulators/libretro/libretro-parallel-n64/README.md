# BR2_PACKAGE_LIBRETRO_PARALLEL_N64

Optimized/rewritten Nintendo 64 emulator made specifically for Libretro. Originally based on Mupen64 Plus.

## Build notes

- ``Version``: f8605345e13c018a30c8f4ed03c05d8fc8f70be8
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 0001-REG.Linux-add-missing-targets.patch
