# Hatari

Hatari emulates Atari ST/STe/TT/Falcon platforms, and REG-Linux captures the classic TOS experience with SDL frontends and key assets.

## Build notes

- `Version`: v2.6.1
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBCAPSIMAGE`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `atarist.hatari.keys` into `/usr/share/evmapy` (or equivalent) and applies `004-no-testing-no-manpages.patch`, `001-tospath.patch`, `003-enforce-lto.patch`, `002-configpath.patch`
