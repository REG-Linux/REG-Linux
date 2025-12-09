# LBreakoutHD

LBreakoutHD recreates the classic Breakout arcade experience with SDL2 acceleration and extended language/media support on REG-Linux.

## Build notes

- `Version`: 1.2 release.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_SDL2_MIXER`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_LIBPNG`, `BR2_TOOLCHAIN_USES_MUSL` helpers.
- `Build helper`: Autotools (`autotools-package`) configured with `--with-sysroot=$(STAGING_DIR)` and `001-fix-configure.patch`.
- `Extras`: uses the standard autotools install path; no additional keys/assets shipped.
