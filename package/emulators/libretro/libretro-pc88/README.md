# BR2_PACKAGE_LIBRETRO_PC88

A port of QUASI88, a PC-8800 series emulator by Showzoh Fukunaga, to the libretro API.

## Build notes

- ``Version``: 42be798db5585f62b4bd34ce49dd1e8063c9d7c1
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-RPi5-tuning.patch
