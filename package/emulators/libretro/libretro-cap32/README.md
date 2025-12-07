# BR2_PACKAGE_LIBRETRO_CAP32

A libretro AMSTRAD CPC emulator core.

## Build notes

- ``Version``: a5d96c5ebbda3bc89a3bd1c1691a20f5eacc232d
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `amstradcpc.keys` into `/usr/share/evmapy` or equivalent; applies patches: 000-rpi_makefile.patch, 002-RPi5-tuning.patch
