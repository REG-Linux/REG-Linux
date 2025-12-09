# Cemu

Cemu runs Wii U titles on REG-Linux by pairing the official emulator with the same middleware used by PC-focused modding communities (https://cemu.info/).

## Build notes

- `Version`: d54fb0ba78ce2ffac3caa399414af19ec1016f05
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_FMT`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_PUGIXML`, `BR2_PACKAGE_RAPIDJSON`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_CONTEXT`, `BR2_PACKAGE_BOOST_PROGRAM_OPTIONS`, `BR2_PACKAGE_BOOST_FILESYSTEM`, `BR2_PACKAGE_BOOST_NOWIDE`, `BR2_PACKAGE_LIBZIP`, `BR2_PACKAGE_GLSLANG`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_ZSTD`, `BR2_PACKAGE_GLM`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBUSB`, `BR2_PACKAGE_WXWIDGETS`, `BR2_PACKAGE_UPOWER`, `BR2_PACKAGE_HIDAPI`, `BR2_PACKAGE_BLUEZ5_UTILS`, `BR2_PACKAGE_WEBP`, `BR2_PACKAGE_WEBP_DEMUX`, `BR2_x86_64 || BR2_aarch64`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: installs `wiiu.keys` into `/usr/share/evmapy` and applies a set of REG-Linux patches (`001-fix-pugixml.patch`, `004-force-no-menubar.patch`, `007-fix-hidapi-include.patch`, `009-fix-findwaylandprotocols-cmake.patch`, `011-fix-apple-aarch64.patch`, `005-disable-cmake-interprocedural-optimization.patch`, `006-fix-keys-path.patch`, `010-fix-warnings-aarch64.patch`, `002-use-userdata.patch`, `008-add-findhidapi-cmake.patch`)
