# Libretro Gearcoleco

The `libretro-gearcoleco` core provides ColecoVision emulation tuned for REG-Linux while reusing the cross-platform Gearcoleco stack.

## Build notes

- `Version`: 1.5.3
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-makefile-additions.patch`
