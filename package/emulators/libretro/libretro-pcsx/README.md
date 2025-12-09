# Libretro PCSX

The `libretro-pcsx` core delivers PlayStation 1 emulation to REG-Linux’s ARM libretro builds with Pi-specific patches already baked in.

## Build notes

- `Version`: 228c14e10e9a8fae0ead8adf30daad2cdd8655b9
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-makefile-rk3326-64.patch` and `001-RPi5-tuning.patch`
