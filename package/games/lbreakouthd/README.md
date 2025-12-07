# LBreakoutHD

Breakout-style arcade game with SDL2 acceleration.

## Build notes
- **Version:** 1.2 release.
- **Config:** selects SDL2, SDL2_image/mixer/ttf, SDL2, and libpng with native language support dependencies;  `BR2_TOOLCHAIN_USES_MUSL` adds config macros for `malloc`/`realloc` detection.
- **Build system:** Autotools (`autotools-package`) with `--with-sysroot=$(STAGING_DIR)` and patched configuration (`001-fix-configure.patch`).
- **Install:** standard `autotools-package` install path; no extra key files included since this is strictly the engine.
