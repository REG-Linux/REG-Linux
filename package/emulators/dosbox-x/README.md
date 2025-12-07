# BR2_PACKAGE_DOSBOX_X

See Buildroot configs for details.

## Build notes

- ``Version``: dosbox-x-v2025.12.01
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_NET, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBOGG, select BR2_PACKAGE_LIBVORBIS, depends on BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Autotools (autotools-package)
- ``Extras``: copies `dos.dosbox-x.keys` into `/usr/share/evmapy` or equivalent; applies patches: 004-aarch64-MT32.patch, 001-sdl-config.patch, 003-dosboxconf.patch, 002-map_mouse.patch, 000-arm_configure.patch
