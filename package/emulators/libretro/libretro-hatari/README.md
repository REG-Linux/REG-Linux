# Libretro Hatari

The `libretro-hatari` core brings Atari ST/STE/TT emulation into REG-Linux with the same SDL/Zlib integration as the standalone Hatari port.

## Build notes

- `Version`: 7008194d3f951a157997f67a820578f56f7feee0
- `Dependencies`: `BR2_PACKAGE_LIBCAPSIMAGE`, `BR2_PACKAGE_ZLIB`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `003-ipf-uaecpu.patch`, `002-floppy-ipf.patch`, `004-fix-gcc14.patch`, `001-pathconfig.patch`, `000-makefile.patch`
