# Xenia Canary

Xenia Canary is the bleeding-edge Xbox 360 emulator that REG-Linux cross-compiles with LLVM/Clang so the latest kernel-driven features are available.

## Build notes

- `Version`: 7d379952f19bded6931f821fad7df29166ec2cc3
- `Dependencies`: `BR2_PACKAGE_PYTHON_TOML`, `BR2_PACKAGE_LIBGTK3`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_BINUTILS`, `BR2_PACKAGE_LIBUNWIND`, `BR2_x86_64`, `BR2_PACKAGE_LLVM`, `BR2_PACKAGE_CLANG`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `xbox360.xenia-canary.keys` into `/usr/share/evmapy` and applies `102-WIP-linux-hid-keyboard-driver.patch`, `000-fix-pkgconfig-lua.patch`, `003-hack-force-stdlibs.patch`, `001-hack-xenia-build-ninja.patch`
