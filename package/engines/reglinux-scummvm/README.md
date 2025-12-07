# REG-Linux ScummVM bundle

This package installs REG-Linux's prebuilt ScummVM bundle, which includes both the standalone ScummVM binary and the libretro core along with their helper assets.

## Configuration
- **Config:** selects SDL2, libmpeg2, libjpeg(+BATO), libogg, libvorbis (or Tremor), FLAC, libmad, libpng, libtheora, FAAD2, freetype, and zlib so the host system still has the codec stack even though this package ships prebuilt binaries.
- **Virtual packages:** defines `BR2_PACKAGE_HAS_SCUMMVM` and `BR2_PACKAGE_HAS_LIBRETRO_SCUMMVM` so that front ends can depend on ScummVM without triggering the source build.

## Build flow
- **Version:** `v2.9.1` release.
- **Deployment:** detects the target architecture (Raspberry Pi series, Rockchip, RK, Tegra, x86_64, RISC-V, etc.), downloads the matching `reglinux-scummvm-<version>-<arch>.tar.gz` archive from `REG-Linux/REG-ScummVM`, and extracts it directly under the target rootfs.
- **Extras:** copies `scummvm.keys` to `/usr/share/evmapy` so the front-end can connect its controller map definitions.
