# Libretro MAME

The `libretro-mame` core keeps REG-Linux’s arcade catalog aligned with upstream MAME (`lrmame0280`) while adding the Batocera-focused INI tweaks and joystick fixes already in the recipe.

## Build notes

- `Version`: lrmame0280
- `Dependencies`: `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_HAS_LIBRETRO_MAME`, and both `BR2_INSTALL_LIBSTDCPP`/`!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies REG-Linux patches (`004-batocera-ini.patch`, `005-flto-auto-genie.patch`, `007-libretro-fix-joystick-4-way-option.patch`, `003-nopch.patch`, `006-libretro-mame-0277-buildfix.patch`, `010-add-prepare-script.patch`, `001-mame-cross-compilation.patch`)
