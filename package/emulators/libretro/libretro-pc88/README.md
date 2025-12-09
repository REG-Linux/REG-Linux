# Libretro PC-88

The `libretro-pc88` core ports QUASI88 (PC-8800 series) into REG-Linux’s libretro tree with Raspberry Pi tuning already applied.

## Build notes

- `Version`: 42be798db5585f62b4bd34ce49dd1e8063c9d7c1
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-RPi5-tuning.patch`
