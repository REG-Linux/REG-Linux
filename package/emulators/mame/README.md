# BR2_PACKAGE_MAME

See Buildroot configs for details.

## Build notes

- ``Version``: gm0280sr221f
- ``Config``: select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_TTF, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_JPEG, select BR2_PACKAGE_SQLITE, select BR2_PACKAGE_FONTCONFIG, select BR2_PACKAGE_RAPIDJSON, select BR2_PACKAGE_EXPAT, select BR2_PACKAGE_GLM, select BR2_PACKAGE_HAS_MAME, depends on BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `mame.mame.keys` into `/usr/share/evmapy` or equivalent; applies patches: 006-fix-sliver.patch, 007-nopch.patch, 002-mame-no-nag-screens.patch, 005-lightgun-udev-driver.patch, 008-default-gun-config.patch, 004-atom-hashfile-additions.patch, 011-switchres-no-xrandr.patch, 009-genie-flto-auto.patch, 010-add-prepare-script.patch, 003-mame-cv1k.patch, 001-mame-cross-compilation.patch
