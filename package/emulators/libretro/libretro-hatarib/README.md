# Libretro HatariB

The `libretro-hatarib` core brings Hatari Atari ST/STE/TT emulation into REG-Linux with the same SDL/Zlib helpers as the standalone Hatari build.

## Build notes

- `Version`: 162d2ed3ee40d8ea394607e7f886a084b660ad5f
- `Dependencies`: `BR2_PACKAGE_LIBCAPSIMAGE`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ZLIB`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `005-cmakeflags.patch`, `002-no-bundled-sdl-zlib.patch`, `004-remove-shorthash.patch`, `003-hatari-cmake-crosscompiling.patch`, `001-fix-soname.patch`
