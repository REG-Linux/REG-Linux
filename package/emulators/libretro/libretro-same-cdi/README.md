# Libretro SAME-CDI

The `libretro-same-cdi` core ports the CD-i emulator (a MAME-derived build) into REG-Linux with common libretro dependencies.

## Build notes

- `Version`: fd72b330452171e950bd08ec4b9fe9acb3446db6
- `Dependencies`: `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_ZSTD`, `BR2_PACKAGE_FLAC`, `BR2_PACKAGE_RAPIDJSON`, `BR2_PACKAGE_PUGIXML`, `BR2_PACKAGE_SQLITE`, `BR2_PACKAGE_EXPAT`, `BR2_PACKAGE_JPEG`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies `001-mame-cross-compilation.patch` and `000-makefile.patch`
