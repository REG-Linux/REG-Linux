# LTris2

Classic Tetris clone packaged for REG-Linux.

## Build notes
- **Version:** 2.0.4 release from SourceForge.
- **Config:** selects SDL2, SDL2_image/mixer/ttf, host-pkgconf, and NLS deps; requires `BR2_USE_MMU` because the upstream build assumes `fork()`.
- **Build system:** Autotools build (`autotools-package`) with `SDL2_CONFIG`, `LIBS`, and `SYSROOT` environment variables wired for cross-compilation.
- **Install:** standard autotools install path; no extra assets beyond the binary.
