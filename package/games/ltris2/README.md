# LTris2

LTris2 brings a classic Tetris clone to REG-Linux with SDL2 display/audio and cross-toolchain support.

## Build notes

- `Version`: 2.0.4 SourceForge release.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_SDL2_MIXER`, `BR2_PACKAGE_SDL2_TTF`, `BR2_USE_MMU`.
- `Build helper`: Autotools (`autotools-package`) with SDL2 env vars (`SDL2_CONFIG`, `LIBS`, `SYSROOT`) tailored for cross builds.
- `Extras`: installs via the standard autotools paths; no extra keys/assets shipped.
