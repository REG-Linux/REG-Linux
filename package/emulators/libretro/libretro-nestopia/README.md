# Libretro Nestopia

The `libretro-nestopia` core adds NES/FDS emulation to REG-Linux with Raspberry Pi tuning already applied.

## Build notes

- `Version`: 3ac52e67c4a7fa696ee37e48bbcec93611277288
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-rpi5-tuning.patch`
