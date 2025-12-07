# BR2_PACKAGE_LIBRETRO_SAME_CDI

A libretro CD-i emulator core (branched from MAME) http://www.libretro.com

## Build notes

- ``Version``: fd72b330452171e950bd08ec4b9fe9acb3446db6
- ``Config``: select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_ZSTD, select BR2_PACKAGE_FLAC, select BR2_PACKAGE_RAPIDJSON, select BR2_PACKAGE_PUGIXML, select BR2_PACKAGE_SQLITE, select BR2_PACKAGE_EXPAT, select BR2_PACKAGE_JPEG
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-mame-cross-compilation.patch, 000-makefile.patch
