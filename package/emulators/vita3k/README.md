# Vita3K

Vita3K brings PlayStation Vita emulation to REG-Linux with SDL2/GTK3 helpers and the latest EVMapy key material.

## Build notes

- `Version`: 3df27923b48c2ddf579b773814e05a315b00196f
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_LIBGTK3`, `BR2_PACKAGE_LIBOGG`, `BR2_PACKAGE_LIBVORBIS`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_FILESYSTEM`, `BR2_PACKAGE_BOOST_SYSTEM`, `BR2_PACKAGE_PYTHON_RUAMEL_YAML`, `BR2_PACKAGE_FMT`, `BR2_PACKAGE_LIBCURL`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `psvita.vita3k.keys` into `/usr/share/evmapy` and applies `006-hack-ffmpeg-git-sha.patch`, `005-fix-header.patch`, `003-disable-nfd-portal.patch`, `001-adjust-paths.patch`, `004-lower-case-vita.patch`
