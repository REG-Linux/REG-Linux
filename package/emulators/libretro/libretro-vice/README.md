# BR2_PACKAGE_LIBRETRO_VICE_XSCPU64

Versatile Commodore 8-bit Emulator Build the standard C64 binary (x64). Build the Commodore 128 binary (x128). Build the VIC-20 binary (xvic). Build the Commodore Plus/4 binary (xplus4). Build the PET/CBM-II binary (xpet). Build the CBM-II variant binary (xcbm2). Build the C64-DTV binary (x64dtv). Build the C64 Single Cycle binary (x64sc) for precise timing. Build the C64 SuperCPU binary (xscpu64).

## Build notes

- ``Version``: e9f8ac034ddef3025f0567768f7af8219f7cfdb8
- ``Config``: depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE, depends on BR2_PACKAGE_LIBRETRO_VICE
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-lto.patch, 000-makefile.patch
