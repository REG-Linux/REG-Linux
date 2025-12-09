# Libretro BlueMSX

The `libretro-bluemsx` core brings MSX/ColecoVision emulation to REG-Linux ARM builds, including the Raspberry Pi tuning applied upstream.

## Build notes

- `Version`: 1f8aeb9ac3f3a4202736ac22e1785f01a834b975
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-RPi5-tuning.patch`
