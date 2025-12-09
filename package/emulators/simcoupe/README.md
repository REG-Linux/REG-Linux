# SimCoupe

SimCoupe adds the Sam Coupe emulator to REG-Linux with the SDL2 frontend and pad configuration patches.

## Build notes

- `Version`: v1.2.15
- `Dependencies`: `BR2_PACKAGE_SDL2`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `samcoupe.keys` into `/usr/share/evmapy` and applies `0002-add-pad-configuration-options.patch`, `0003-use-pad-configuration.patch`, `0001-aarch64-little-endian.patch`
