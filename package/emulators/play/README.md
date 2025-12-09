# Play!

The `play` port ships the PlayStation 2 emulator Play! (https://purei.org/) with Qt6, OpenGL, and EVMapy keys so REG-Linux stays compatible with PS2 titles.

## Build notes

- `Version`: 0.71
- `Dependencies`: `BR2_PACKAGE_PCRE2`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_LIBCURL_OPENSSL`, `BR2_PACKAGE_LIBGLEW`/`BR2_PACKAGE_LIBGLU` (when `BR2_PACKAGE_REGLINUX_XWAYLAND`), `BR2_PACKAGE_OPENAL`, `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_SQLITE`, `BR2_PACKAGE_ECM`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `ps2.play.keys` and `namco2x6.keys` into `/usr/share/evmapy` and applies `002-fix-arcadepath.patch`, `003-gcc13-fix.patch`, `001-fpic.patch`, `004-fix-zlib-ng.patch`
