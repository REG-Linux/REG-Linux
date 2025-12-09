# openMSX

The `openmsx` package ensures REG-Linux ships the perfectly-tuned MSX emulator along with SDL2, audio, and OpenGL helpers.

## Build notes

- `Version`: RELEASE_19_1
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBOGG`, `BR2_PACKAGE_LIBVORBIS`, `BR2_PACKAGE_LIBTHEORA`, `BR2_PACKAGE_LIB`, `BR2_PACKAGE_TCL`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_LIBGLEW` (when `BR2_PACKAGE_HAS_LIBGL`), `BR2_PACKAGE_FREETYPE`
- `Build helper`: Autotools (`autotools-package`)
- `Extras`: applies `001-user-dir.patch`, `002-filepool.patch`, `003-fix-gcc14.patch`
