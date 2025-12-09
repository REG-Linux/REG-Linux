# Libretro Gambatte

The `libretro-gambatte` core delivers Game Boy/Game Boy Color emulation under REG-Linux with Raspberry Pi tuning baked in.

## Build notes

- `Version`: 5707c1806fbca784c22550db1fa2ce7ed646df09
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-RPi5-tuning.patch`
