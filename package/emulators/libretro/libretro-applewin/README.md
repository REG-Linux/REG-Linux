# BR2_PACKAGE_LIBRETRO_APPLEWIN

See Buildroot configs for details.

## Build notes

- ``Version``: $(APPLEWIN_VERSION)
- ``Config``: select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_PROGRAM_OPTIONS, select BR2_PACKAGE_MINIZIP_ZLIB, select BR2_PACKAGE_SLIRP, select BR2_PACKAGE_LIBPCAP, select BR2_PACKAGE_LIBYAML, select BR2_PACKAGE_HOST_XXD
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 003-no-test.patch, 004-enforce-lto.patch, 001-enable-opengles-option.patch, 002-force-static-linking.patch
