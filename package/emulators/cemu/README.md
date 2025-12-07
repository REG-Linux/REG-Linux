# BR2_PACKAGE_CEMU

Cemu is a Wii U emulator that now runs natively on Linux. https://cemu.info/

## Build notes

- ``Version``: d54fb0ba78ce2ffac3caa399414af19ec1016f05
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_FMT, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_PUGIXML, select BR2_PACKAGE_RAPIDJSON, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_CONTEXT, select BR2_PACKAGE_BOOST_PROGRAM_OPTIONS, select BR2_PACKAGE_BOOST_FILESYSTEM, select BR2_PACKAGE_BOOST_NOWIDE, select BR2_PACKAGE_LIBZIP, select BR2_PACKAGE_GLSLANG, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_ZSTD, select BR2_PACKAGE_GLM, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBUSB, select BR2_PACKAGE_WXWIDGETS, select BR2_PACKAGE_UPOWER                   # required by some cemuhook servers, select BR2_PACKAGE_HIDAPI, select BR2_PACKAGE_BLUEZ5_UTILS, select BR2_PACKAGE_WEBP, select BR2_PACKAGE_WEBP_DEMUX, depends on BR2_x86_64 || BR2_aarch64
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `wiiu.keys` into `/usr/share/evmapy` or equivalent; applies patches: 001-fix-pugixml.patch, 004-force-no-menubar.patch, 007-fix-hidapi-include.patch, 009-fix-findwaylandprotocols-cmake.patch, 011-fix-apple-aarch64.patch, 005-disable-cmake-interprocedural-optimization.patch, 006-fix-keys-path.patch, 010-fix-warnings-aarch64.patch, 002-use-userdata.patch, 008-add-findhidapi-cmake.patch
