# BR2_PACKAGE_APPLEWIN

See Buildroot configs for details.

## Build notes

- ``Version``: bc0b9c1e7e43a7bcc916d84297a2d3d7b1d3a84f
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_IMAGE, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_PROGRAM_OPTIONS, select BR2_PACKAGE_MINIZIP_ZLIB, select BR2_PACKAGE_SLIRP, select BR2_PACKAGE_LIBPCAP, select BR2_PACKAGE_LIBYAML, select BR2_PACKAGE_HOST_XXD
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 002-no-test.patch, 001-enable-opengles-option.patch
