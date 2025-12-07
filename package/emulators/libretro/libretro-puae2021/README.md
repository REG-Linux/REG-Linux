# BR2_PACKAGE_LIBRETRO_PUAE2021

2021 libretro AMIGA emulator core for ARM. http://www.libretro.com https://github.com/libretro/libretro-uae/tree/2.6.1

## Build notes

- ``Version``: 71d105288333ce63aeaaa20ebb1dfe07c24d050f
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 000-rpi_makefile.patch, 002-isoc99math.patch, 001-capsimg-path.patch, 003-gcc14-hack.patch
