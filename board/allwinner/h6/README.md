# REG-Linux · Allwinner H6 Boards

Everything in this directory is used by Buildroot to assemble REG-Linux images for Allwinner H6 based single-board computers.
Each board folder provides the boot assets (kernel entry, post-image script, disk layout) that Buildroot consumes, while the sibling directories collect tweaks that apply to every H6 target.

---

## Quick Start

1. Point your Buildroot configuration to one of the targets under `board/allwinner/h6/<board>/`.
2. Set the common helpers:
   - `BR2_ROOTFS_OVERLAY="board/allwinner/h6/fsoverlay"`
   - `BR2_ROOTFS_POST_IMAGE_SCRIPT="board/allwinner/h6/<board>/create-boot-script.sh"`
3. Build as usual (`make`). The post-image script copies the kernel, initrd, update bundle, modules, firmware and DTB into `${REGLINUX_BINARIES_DIR}/boot`.
4. `genimage --config board/allwinner/h6/<board>/genimage.cfg` (invoked automatically by REG-Linux) emits `reglinux.img`, ready to flash with `dd` or `bmaptool`.

Need to swap a kernel or DTB quickly? Mount the generated `boot.vfat` and replace `/boot/linux` or `/boot/*.dtb` without touching the root filesystem image.

---

## Directory Map

| Path | Purpose |
| ---- | ------- |
| `fsoverlay/` | Shared rootfs overlay (fan/BT helpers, install-to-eMMC script, ALSA defaults, temperature monitors). |
| `patches/arm-trusted-firmware/` | Patches applied to TF-A before packing (keeps unused regulators disabled to avoid boot hangs). |
| `build-uboot.sh` | Shared helper that rebuilds TF-A (`sun50i_h6`) plus U-Boot 2025.01 and stores the SPL under `reglinux/uboot-<target>/`. |
| `<board>/boot/` | Extlinux stanza for the board and, when needed, extra boot scripts. |
| `<board>/create-boot-script.sh` | Post-image helper that invokes `../build-uboot.sh`, then stages kernel, initrd, update bundle, firmware, modules, DTB, and extlinux. |
| `<board>/genimage.cfg` | Disk layout describing the FAT32 boot partition, userdata EXT4, and the U-Boot SPL injection offset. |

---

## Board Reference

| Board dir | Target devices | Device tree staged to `/boot` | SPL injected by `genimage` | Notes |
| --------- | -------------- | ----------------------------- | ------------------------- | ----- |
| `orangepi-3/` | Orange Pi 3 (Allwinner H6) | `sun50i-h6-orangepi-3.dtb` | `../uboot-orangepi-3/u-boot-sunxi-with-spl.bin` @8 KiB | Use this when building for the original Orange Pi 3 with onboard eMMC. |
| `orangepi-3-lts/` | Orange Pi 3 LTS | `sun50i-h6-orangepi-3-lts.dtb` | `../uboot-orangepi-3-lts/u-boot-sunxi-with-spl.bin` @8 KiB | Identical boot flow, but the DTB enables the revised PMIC/supply tree. |
| `orangepi-one-plus/` | Orange Pi One Plus | `sun50i-h6-orangepi-one-plus.dtb` | `../uboot-orangepi-one-plus/u-boot-sunxi-with-spl.bin` @8 KiB | Smallest H6 board; only the DTB/SPL path differs from the other targets. |

Each table entry contains a full boot stack: `create-boot-script.sh` rebuilds TF-A + U-Boot via `../build-uboot.sh`, copies the matching DTB into `/boot`, the extlinux stanza points at it, and `genimage.cfg` injects the proper SPL binary. To add another H6 platform, clone the closest board directory, adjust the DTB file name, set the new `UBOOT_DEFCONFIG`/`UBOOT_TARGET` in the staging script, and update `genimage.cfg` to reference the corresponding `../uboot-<target>/...` artifact.

---

### Shared Rootfs Overlay (`fsoverlay/`)

- `usr/bin/install2emmc` flashes the generated image from SD to onboard eMMC directly on the device.
- `usr/bin/{cpu,gpu}temp` and `usr/bin/hciattach_opi` expose temperature monitoring and BT bring-up helpers for panel UIs.
- `etc/modules.conf` and ALSA snippets preload the audio and Wi-Fi kernel modules that H6 boards expect at boot.

Update or extend this overlay whenever you need a file to land on every H6 target.

---

### Trusted Firmware Patch Stack

`patches/arm-trusted-firmware/0001-sunxi-Don-t-enable-referenced-regulators.patch` is applied by `build-uboot.sh` before Trusted Firmware-A is rebuilt. Keep the description in this README aligned with any additional patches you introduce so contributors immediately know why they exist.
