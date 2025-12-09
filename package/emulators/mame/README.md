# MAME

The standalone `mame` port feeds REG-Linux’s arcade catalog with upstream `gm0280sr221f` plus Batocera-style tweaks so the distro ships a ready-to-run `mame` binary.

## Build notes

- `Version`: gm0280sr221f
- `Dependencies`: `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_TTF`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_JPEG`, `BR2_PACKAGE_SQLITE`, `BR2_PACKAGE_FONTCONFIG`, `BR2_PACKAGE_RAPIDJSON`, `BR2_PACKAGE_EXPAT`, `BR2_PACKAGE_GLM`, `BR2_PACKAGE_HAS_MAME`, `BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `mame.mame.keys` into `/usr/share/evmapy` and applies REG-Linux patches (`006-fix-sliver.patch`, `007-nopch.patch`, `002-mame-no-nag-screens.patch`, `005-lightgun-udev-driver.patch`, `008-default-gun-config.patch`, `004-atom-hashfile-additions.patch`, `011-switchres-no-xrandr.patch`, `009-genie-flto-auto.patch`, `010-add-prepare-script.patch`, `003-mame-cv1k.patch`, `001-mame-cross-compilation.patch`)
