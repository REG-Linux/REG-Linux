# Eden

Eden ships the Nintendo Switch emulator to REG-Linux with Boost/Qt6 tooling and additional patches so modern titles behave on both x86_64 and ARM hosts.

## Build notes

- `Version`: v0.0.4-rc3
- `Dependencies`: `BR2_PACKAGE_JSON_FOR_MODERN_CPP`, `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_FMT`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_CONTEXT`, `BR2_PACKAGE_BOOST_FILESYSTEM`, `BR2_PACKAGE_ZSTD`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBZIP`, `BR2_PACKAGE_LIBUSB`, `BR2_PACKAGE_LZ4`, `BR2_PACKAGE_CATCH2`, `BR2_PACKAGE_OPUS`, `BR2_PACKAGE_ENET`, `BR2_PACKAGE_GAMEMODE`, `BR2_PACKAGE_LIBVA`, `BR2_PACKAGE_REGLINUX_XWAYLAND`, `BR2_PACKAGE_FFMPEG`, `BR2_PACKAGE_HOST_YASM` (when `BR2_x86_64`), `BR2_PACKAGE_MBEDTLS`, plus `BR2_x86_64 || BR2_aarch64`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `switch.eden.keys` into `/usr/share/evmapy` (or equivalent) and applies REG-Linux patches (`001-fix-sse2neon.patch`, `004-format_custom.patch`, `002-adjust-paths.patch`, `003-external-nx-tzdb-prebuilt.patch`)
