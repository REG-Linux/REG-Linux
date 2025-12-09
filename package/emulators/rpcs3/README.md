# RPCS3

RPCS3 delivers PlayStation 3 emulation to REG-Linux with broad Qt6/SDL3 support and the EVMapy key bundle.

## Build notes

- `Version`: v0.0.38
- `Dependencies`: `BR2_HOST_CMAKE_AT_LEAST_3_24`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_LLVM`, `BR2_PACKAGE_FFMPEG_SWSCALE`, `BR2_PACKAGE_LIBEVDEV`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBGLEW`, `BR2_PACKAGE_LIBGLU`, `BR2_PACKAGE_LIBUSB`, `BR2_PACKAGE_LIBXML2`, `BR2_PACKAGE_MESA3D`, `BR2_PACKAGE_NCURSES`, `BR2_PACKAGE_OPENAL`, `BR2_PACKAGE_PUGIXML`, `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_RTMIDI`, `BR2_PACKAGE_RTMPDUMP`, `BR2_PACKAGE_SDL3`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_ZSTD`, `BR2_TOOLCHAIN_GCC_AT_LEAST_8`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: installs `evmapy.keys` into `/usr/share/evmapy` and applies patches (`013-gun-support.patch`, `010-padsevdev.patch`, `014-gun-mapping.patch`, `012-savestate-location.patch`, `006-no-firmware-confirmation.patch`, `004-fix-iconv.patch`, `007-fix-screenshot-directory.patch`, `001-fix-libusb.patch`)
