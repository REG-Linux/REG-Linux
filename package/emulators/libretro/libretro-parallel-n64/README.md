# Libretro Parallel N64

The `libretro-parallel-n64` core is REG-Linux’s optimized Nintendo 64 backend, maintaining the parallel-rice rework for libretro builds.

## Build notes

- `Version`: f8605345e13c018a30c8f4ed03c05d8fc8f70be8
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `0001-REG.Linux-add-missing-targets.patch`
