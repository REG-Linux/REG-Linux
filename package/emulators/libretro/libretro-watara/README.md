# Libretro Watara

The `libretro-watara` core brings the Watara Supervision/Champion emulation into REG-Linux with Raspberry Pi tuning.

## Build notes

- `Version`: ad87bc6068ef126e48339b440465fb0bf5a2794f
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-rpi5-tuning.patch`
