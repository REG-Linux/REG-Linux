# Libretro DOSBox Pure

The `libretro-dosbox-pure` core brings DOS emulation to REG-Linux’s libretro stack with Raspberry Pi patching.

## Build notes

- `Version`: 1.0-preview4
- `Dependencies`: supports both `BR2_INSTALL_LIBSTDCPP` and `!BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `000-rpi_makefile.patch`
