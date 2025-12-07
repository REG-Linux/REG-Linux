# BR2_PACKAGE_DOSBOX_STAGING

See Buildroot configs for details.

## Build notes

- ``Version``: v0.82.2
- ``Config``: select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_SPEEXDSP, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_IMAGE, select BR2_PACKAGE_SDL2_NET, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBOGG, select BR2_PACKAGE_LIBVORBIS, select BR2_PACKAGE_OPUS, select BR2_PACKAGE_OPUSFILE, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_SLIRP, select BR2_PACKAGE_IIR, depends on BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Meson (meson-package)
- ``Extras``: applies patches: 001-disable-pagesize-testing.patch, 000-no_wrap.patch, 002-disable-neon-sse2-ssse3-testing.patch
