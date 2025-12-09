# Libretro Genesis Plus GX

The `libretro-genesisplusgx` core maintains REG-Linux’s Sega 8/16-bit compatibility layer on ARM with the upstream Genesis Plus GX renderer.

## Build notes

- `Version`: eca60fff0d097150e0d8ec3a160543ca2c31a74a
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-makefile-additions.patch`
