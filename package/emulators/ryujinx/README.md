# BR2_PACKAGE_RYUJINX

Ryujinx is an open-source Nintendo Switch emulator created by gdkchan and written in C sharp.

## Build notes

- ``Version``: 1.3.3
- ``Config``: depends on BR2_x86_64 || BR2_aarch64, depends on BR2_PACKAGE_HAS_LIBGL || BR2_PACKAGE_REGLINUX_VULKAN
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `switch.ryujinx.keys` into `/usr/share/evmapy` or equivalent
