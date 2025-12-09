# Libretro Cap32

The `libretro-cap32` core emulates the Amstrad CPC, delivering the key handling and Raspberry Pi patches REG-Linux needs for CPC hardware.

## Build notes

- `Version`: a5d96c5ebbda3bc89a3bd1c1691a20f5eacc232d
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `amstradcpc.keys` into `/usr/share/evmapy` (or equivalent) and applies `000-rpi_makefile.patch`, `002-RPi5-tuning.patch`
