# BR2_PACKAGE_XENIA_CANARY

Xenia is an open source research project for emulating Xbox 360 games on modern PCs. This is the bleeding edge canary release. https://xenia.jp/

## Build notes

- ``Version``: 7d379952f19bded6931f821fad7df29166ec2cc3
- ``Config``: select BR2_PACKAGE_PYTHON_TOML, select BR2_PACKAGE_LIBGTK3, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_BINUTILS, select BR2_PACKAGE_LIBUNWIND, depends on BR2_x86_64, depends on BR2_PACKAGE_LLVM, depends on BR2_PACKAGE_CLANG
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `xbox360.xenia-canary.keys` into `/usr/share/evmapy` or equivalent; applies patches: 102-WIP-linux-hid-keyboard-driver.patch, 000-fix-pkgconfig-lua.patch, 003-hack-force-stdlibs.patch, 001-hack-xenia-build-ninja.patch
