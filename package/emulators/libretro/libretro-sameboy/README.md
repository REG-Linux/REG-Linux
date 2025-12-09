# Libretro SameBoy

The `libretro-sameboy` core runs the SameBoy Game Boy/Game Boy Color emulator under REG-Linux with RGBDS/XXD tooling and the same libstdc++ toggles.

## Build notes

- `Version`: v1.0.2
- `Dependencies`: `BR2_PACKAGE_RGBDS`, `BR2_PACKAGE_XXD`, supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-makefile_hexdump.patch`
