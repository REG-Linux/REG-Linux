# BR2_PACKAGE_VICE_XSCPU64

Build the standard C64 binary (x64). Build the Commodore 128 binary (x128). Build the VIC-20 binary (xvic). Build the Commodore Plus/4 binary (xplus4). Build the PET/CBM-II binary (xpet). Build the CBM-II variant binary (xcbm2). Build the standard C64-DTV binary (x64dtv). Build the C64 Single Cycle binary (x64sc) for precise timing. Build the C64 SuperCPU binary (xscpu64).

## Build notes

- ``Version``: 3.9
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_SDL2_IMAGE, select BR2_PACKAGE_PNG, select BR2_PACKAGE_JPEG, select BR2_PACKAGE_GIFLIB, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LAME, select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_LIBVORBIS, select BR2_PACKAGE_MPG123, select BR2_PACKAGE_FLAC, select BR2_PACKAGE_HOST_XA, select BR2_PACKAGE_HOST_DOS2UNIX, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE, depends on BR2_PACKAGE_VICE
- ``Build helper``: Autotools (autotools-package)
- ``Extras``: copies `c64.vice.keys, c128.vice.keys` into `/usr/share/evmapy` or equivalent; applies patches: 000-fix-segfault.patch
