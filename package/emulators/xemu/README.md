# Xemu

Xemu packages the Xbox original emulator (QEMU-based) so REG-Linux ships chihiro/xbox keysets and optional Vulkan hooks.

## Build notes

- `Version`: v0.8.114
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_LIBSAMPLERATE`, `BR2_PACKAGE_SLIRP`, `BR2_PACKAGE_PYTHON_PYYAML`, `BR2_PACKAGE_LIBPCAP`, `BR2_PACKAGE_HOST_LIBCURL`, `BR2_PACKAGE_HOST_LIBCURL_CURL`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_JSON_FOR_MODERN_CPP`, `BR2_PACKAGE_HOST_CMAKE`, `BR2_TOOLCHAIN_GCC_AT_LEAST_8`
- `Build helper`: Autotools (`autotools-package`)
- `Extras`: copies `chihiro.xemu.keys` and `xbox.xemu.keys` into `/usr/share/evmapy` and applies `000-fix-xemu-version-sh.patch`, `002-eeprom-path.patch`, `003-hide-menu.patch`, `004-make-vulkan-optional.patch`, `001-fix-optionrom-makefile.patch`
