# BR2_PACKAGE_XEMU

Xbox (og) emulator based on QEMU https://xemu.app/

## Build notes

- ``Version``: v0.8.114
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_LIBSAMPLERATE, select BR2_PACKAGE_SLIRP, select BR2_PACKAGE_PYTHON_PYYAML, select BR2_PACKAGE_LIBPCAP, select BR2_PACKAGE_HOST_LIBCURL, select BR2_PACKAGE_HOST_LIBCURL_CURL, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_JSON_FOR_MODERN_CPP, select BR2_PACKAGE_HOST_CMAKE, depends on BR2_TOOLCHAIN_GCC_AT_LEAST_8
- ``Build helper``: Autotools (autotools-package)
- ``Extras``: copies `chihiro.xemu.keys, xbox.xemu.keys` into `/usr/share/evmapy` or equivalent; applies patches: 000-fix-xemu-version-sh.patch, 002-eeprom-path.patch, 003-hide-menu.patch, 004-make-vulkan-optional.patch, 001-fix-optionrom-makefile.patch
