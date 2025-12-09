# melonDS

The `melonds` port provides REG-Linux with Nintendo DS emulation, tracking the Kuribo64 tree while wiring Qt6, SDL2, and networking helpers.

## Build notes

- `Version`: 1.1
- `Dependencies`: `BR2_PACKAGE_LIBARCHIVE`, `BR2_PACKAGE_LIBEPOXY`, `BR2_PACKAGE_LIBENET`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SLIRP`, `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_ECM`, `BR2_PACKAGE_FAAD2`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `nds.melonds.keys` into `/usr/share/evmapy` and applies `001-legacy-config.patch`
