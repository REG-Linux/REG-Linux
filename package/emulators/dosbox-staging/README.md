# DOSBox Staging

DOSBox Staging delivers the community-maintained fork of DOSBox with async audio and better SIMD support, built for REG-Linux via meson for optimized ARM/desktop hosts.

## Build notes

- `Version`: v0.82.2
- `Dependencies`: `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_SPEEXDSP`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_PACKAGE_SDL2_NET`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBOGG`, `BR2_PACKAGE_LIBVORBIS`, `BR2_PACKAGE_OPUS`, `BR2_PACKAGE_OPUSFILE`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_SLIRP`, `BR2_PACKAGE_IIR`, `BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Meson (`meson-package`)
- `Extras`: applies REG-Linux patches (`001-disable-pagesize-testing.patch`, `000-no_wrap.patch`, `002-disable-neon-sse2-ssse3-testing.patch`)
