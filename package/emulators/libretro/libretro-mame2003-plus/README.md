# Libretro MAME2003-Plus

The `libretro-mame2003-plus` core keeps REG-Linux's ARM arcade support aligned with MAME2003-Plus using both libstdc++ build paths plus the usual LTO/makefile fixes.

## Build notes

- `Version`: 62c7089644966f6ac5fc79fe03592603579a409d
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-enable-lto.patch` and `000-makefile.patch`
