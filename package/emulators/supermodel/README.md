# Supermodel

The `supermodel` port brings Sega Model 3 arcade emulation to REG-Linux with SDL2 networking, GL helpers, and the Model 3 key set.

## Build notes

- `Version`: v0.3a-git-4e5905f
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_NET`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBGLEW`, `BR2_PACKAGE_LIBGLU`, `BR2_PACKAGE_LIBZIP`, `BR2_INSTALL_LIBSTDCPP`, `BR2_PACKAGE_XORG7`, `BR2_PACKAGE_HAS_LIBGL`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `model3.supermodel.keys` into `/usr/share/evmapy` and applies `001-folder-directory.patch`, `003-cross-compile.patch`, `005-evdev-for-guns.patch`, `004-game-settings.patch`, `002-updatetemplate.patch`
