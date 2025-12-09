# Libretro Gearsystem

The `libretro-gearsystem` core streams Sega Master System/Game Gear/SG-1000 emulation into REG-Linux, taking the cross-platform Gearsystem stack and applying the distro’s RPi-friendly tweaks.

## Build notes

- `Version`: 3.8.5
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-makefile-additions.patch`
