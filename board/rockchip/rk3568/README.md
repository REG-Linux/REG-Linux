# Rockchip RK3568 board support

This directory contains the board-specific pieces that RegLinux needs to boot on Rockchip RK3568 devices. Each subdirectory provides the files (boot scripts, extlinux configs, device trees and optional scripts) required by `create-boot-script.sh`, along with helper scripts that package or build the bootloader for that board.

## Board-specific directories
- `anbernic-rgxx3/`  
  Contains the `boot` tree (`boot.cmd`, `boot.scr`, `extlinux.conf`). `create-boot-script.sh` now copies the shared `build-uboot.sh` helper into `reglinux/` and builds `anbernic-rgxx3-rk3566_defconfig` + `rkbin` blobs before staging the built `u-boot-rockchip.bin`, `u-boot.itb`, the kernel image (`Image`), squashfs/initrd, and all of the supported Anbernic DTBs.
```

`firefly-station-m2/` and `firefly-station-p2/`  
  Each board directory stores only `boot/extlinux.conf`, `genimage.cfg`, and scripts that copy prebuilt `idbloader.img`/`uboot.img` from `IMAGES_DIR/uboot-*` into `reglinux/uboot-*`. They do not rebuild U-Boot locally.

`odroid-m1/` and `odroid-m1s/`  
  These folders now use the shared helper (`build-uboot.sh`). The helper downloads U-Boot 2025.10, reuses the pinned `rkbin` commit, applies `patches/uboot/*.patch`, and produces `uboot-odroid-m1/`/`uboot-odroid-m1s/` alongside `reglinux`. `create-boot-script.sh` reuses that output plus the board extlinux/payload assets.

`rock-3a/` and `rock-3c/`  
  These boards also run through the shared helper, building their defconfigs once per run and copying the resulting `u-boot-rockchip.bin` into the boot partition. `rock-3a` additionally ships a prebuilt `rock3a-uboot.img`, and its helper passes `SYSROOT="${HOST_DIR}"` to `make`.

The new `build-uboot.sh` helper caches the tarball + `rkbin` repo under `output/rk3568/images/build-uboot-cache/`, applies the shared patch queue plus any per-board patches, and copies the resulting `u-boot-rockchip.bin` (and, when present, `u-boot.itb`) into `output/rk3568/images/uboot-<target>/`, which is what `genimage.cfg` expects (it now reads `../../uboot-<target>/...`). Firefly boards still bypass this by copying the prebuilt blobs from `IMAGES_DIR/uboot-*`.

Each board's `create-boot-script.sh` is called with the standard arguments (`HOST_DIR`, `BOARD_DIR`, `BUILD_DIR`, `BINARIES_DIR`, `TARGET_DIR`, `REGLINUX_BINARIES_DIR`). It copies the kernel `Image`, firmware/modules/rescue bundles, the rootfs (`rootfs.cpio.lz4`, `rootfs.squashfs`), the matching dtb, the board `extlinux.conf`, `boot.scr`, and `boot-logo` into the final `/boot` and `/boot/extlinux` trees that `genimage` will package.

## Shared overlays and kernel configuration
- `fsoverlay/` contains auxiliary utilities and ALSA configuration that are merged into the rootfs: `usr/bin/cputemp` and `usr/bin/gputemp` (useful temperature reporters on RK3568 SBCs) plus the ALSA cards directory under `usr/share/alsa/cards/`.
- `linux-defconfig.config` is the kernel configuration (Linux 6.6.40) used by Buildroot for RK3568 builds, with the local version string suffixed `-reglinux`.
- `linux_patches/` holds kernel patches that tweak RK3568 input and power handling: renaming the RK817 battery node, adapting single-ADC joypad setups, and updating the input handling for the RG353/503 variants and related devices, along with the USB bandwidth cap tweak for Sinden streaming cameras.
- `patches/uboot/` currently carries `dts-anbernic-rgxx3-singleadc-joypad.patch`, which adjusts the Anbernic tree for the single-ADC inputs.

## Building and image creation
1. Ensure Buildroot produces the generic RK3568 outputs (`Image`, `rootfs.cpio.lz4`, `rootfs.squashfs`, modules, firmware, rescue, `rk3568-*.dtb` and the `uboot-*` binaries when required).
2. Each board's `build-uboot.sh` lives under the board directory and is invoked by `create-boot-script.sh`. It either copies prebuilt `idbloader`/`uboot` images (Firefly) or downloads U-Boot, applies the patches, and compiles the defconfig for that board using `${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-` as the toolchain prefix.
3. `create-boot-script.sh` gathers those artifacts into `REGLINUX_BINARIES_DIR/boot` and `…/boot/extlinux` and ensures the board-specific `extlinux.conf`, `boot.scr`, and bootlogo are present for `genimage`.
4. Finally, `genimage` runs using the `genimage.cfg` found in the board directory to produce a bootable SD card image.

## Notes
- The `genimage.cfg` files in each board directory describe the partition layout required by that hardware and expect the helper scripts to have populated the `REGLINUX_BINARIES_DIR` structure shown above.
- **Anbernic RG353 (and other RG353xx devices running Android):** these boards fail to boot RegLinux unless the stock Android installation is completely wiped first.
