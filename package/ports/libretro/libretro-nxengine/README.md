# libretro-nxengine

Builds the Cave Story core (`nxengine-libretro`) for the libretro ecosystem.

## Build notes
- **Version:** commit `9adc032a5f6aa913d71d22042bb72cb11cf0f4a2` (Oct 2024).
- **Config:** requires a C++ toolchain and selects `BR2_PACKAGE_LIBRETRO_NXENGINE`.
- **Build system:** runs the upstream Makefile with a `platform` variable that detects Raspberry Pi models (armv, `rpi1`, `rpi2`, `rpi3_64`, `rpi4_64`, `rpi5_64`) or falls back to `unix` on AArch64.
- **Install:** installs `nxengine_libretro.so` under `/usr/lib/libretro`.
