# REG-Linux MAME

The `reglinux-mame` package mirrors the distro’s patched MAME build (`0.280`) for direct shipping alongside the libretro core and standalone emulator.

## Build notes

- `Version`: 0.280
- `Dependencies`: `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_JPEG`, `BR2_PACKAGE_SQLITE`, `BR2_PACKAGE_FONTCONFIG`, `BR2_PACKAGE_RAPIDJSON`, `BR2_PACKAGE_EXPAT`, `BR2_PACKAGE_GLM`, `BR2_PACKAGE_HAS_MAME`, `BR2_PACKAGE_HAS_LIBRETRO_MAME`
- `Build helper`: Generic/Makefile (`generic-package`)
