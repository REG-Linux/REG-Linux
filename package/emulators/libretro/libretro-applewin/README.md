# Libretro AppleWin

The `libretro-applewin` core wraps the AppleWin Apple II emulator for REG-Linux, requiring the same Qt/Boost helpers as the standalone AppleWin build.

## Build notes

- `Version`: `$(APPLEWIN_VERSION)`
- `Dependencies`: `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_PROGRAM_OPTIONS`, `BR2_PACKAGE_MINIZIP_ZLIB`, `BR2_PACKAGE_SLIRP`, `BR2_PACKAGE_LIBPCAP`, `BR2_PACKAGE_LIBYAML`, `BR2_PACKAGE_HOST_XXD`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `003-no-test.patch`, `004-enforce-lto.patch`, `001-enable-opengles-option.patch`, `002-force-static-linking.patch`
