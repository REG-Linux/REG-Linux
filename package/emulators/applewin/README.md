# AppleWin

AppleWin emulates Apple II hardware on Linux, exposing the same mix of classic ROMs and disk images that REG-Linux needs to boot Apple II software through its SDL frontend.

## Build notes

- `Version`: `bc0b9c1e7e43a7bcc916d84297a2d3d7b1d3a84f`
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_PROGRAM_OPTIONS`, `BR2_PACKAGE_MINIZIP_ZLIB`, `BR2_PACKAGE_SLIRP`, `BR2_PACKAGE_LIBPCAP`, `BR2_PACKAGE_LIBYAML`, `BR2_PACKAGE_HOST_XXD`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: applies `002-no-test.patch` and `001-enable-opengles-option.patch`
