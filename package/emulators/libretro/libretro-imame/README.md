# Libretro iMAME

The `libretro-imame` core wraps the iMAME4all arcade emulator for REG-Linux ARM builds with Pi-friendly patching.

## Build notes

- `Version`: 2ec60f6e1078cf9ba173e80432cc28fd4eea200f
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-rpi_makefile.patch`
