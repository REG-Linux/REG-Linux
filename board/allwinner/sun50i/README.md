# REG-Linux - Allwinner sun50i (H5 + H6)

This directory unifies the H5 and H6 board stacks into a single sun50i target.
Each board folder provides the boot assets Buildroot expects, while common
filesystem tweaks and package patches live alongside them.

---

## Quick Start

1. Select the board under `board/allwinner/sun50i/<board>/` in your Buildroot config.
2. Ensure the build uses:
   - `BR2_ROOTFS_OVERLAY="board/allwinner/sun50i/fsoverlay"`
   - `BR2_ROOTFS_POST_IMAGE_SCRIPT="board/allwinner/sun50i/<board>/create-boot-script.sh"`
3. Run your usual `make`. The post-image script stages kernel, initrd, DTB, and
   update bundles in `${REGLINUX_BINARIES_DIR}/boot`.
4. `genimage --config board/allwinner/sun50i/<board>/genimage.cfg` (invoked by
   REG-Linux) emits `reglinux.img`, ready to flash with `dd` or `bmaptool`.

For rapid iteration, mount the generated `boot.vfat` and swap `/boot/linux` or
`/boot/*.dtb` without rebuilding the full image.

---

## Directory Map

| Path | Purpose |
| ---- | ------- |
| `fsoverlay/` | Root filesystem overlay applied to every sun50i target. |
| `patches/` | Package-specific fixes required by these boards. |
| `patches/arm-trusted-firmware/` | TF-A patches applied before building BL31. |
| `patches/u-boot/` | Shared U-Boot patches for H5 and H6 boards. |
| `build-uboot.sh` | Shared helper that rebuilds TF-A (H5 uses `sun50i_a64`, H6 uses `sun50i_h6`) plus U-Boot 2025.01 and stores the SPL under `reglinux/uboot-<target>/`. |
| `uboot.config.fragment` | Common U-Boot config fragment (boot delay, ident string). |
| `<board>/boot/` | Extlinux stanza for the board (and optional extra scripts). |
| `<board>/create-boot-script.sh` | Post-image helper that invokes `../build-uboot.sh`, then stages kernel, initrd, update bundle, firmware, modules, DTB, and extlinux. |
| `<board>/genimage.cfg` | Disk layout describing the FAT32 boot partition, userdata EXT4, and the U-Boot SPL injection offset. |

---

## Board Reference

| Board dir | SoC | Device tree staged to `/boot` | SPL injected by `genimage` | Notes |
| --------- | --- | ----------------------------- | ------------------------- | ----- |
| `orangepi-pc2/` | H5 | `sun50i-h5-orangepi-pc2.dtb` | `../uboot-orangepi-pc2/u-boot-sunxi-with-spl.bin` @8 KiB | Orange Pi PC2. |
| `tritium-h5/` | H5 | `sun50i-h5-libretech-all-h3-cc.dtb` | `../uboot-tritium-h5/u-boot-sunxi-with-spl.bin` @8 KiB | Libretech Tritium H5 (ALL-H3-CC). |
| `orangepi-3/` | H6 | `sun50i-h6-orangepi-3.dtb` | `../uboot-orangepi-3/u-boot-sunxi-with-spl.bin` @8 KiB | Orange Pi 3 with onboard eMMC. |
| `orangepi-3-lts/` | H6 | `sun50i-h6-orangepi-3-lts.dtb` | `../uboot-orangepi-3-lts/u-boot-sunxi-with-spl.bin` @8 KiB | Orange Pi 3 LTS (revised PMIC/supply tree). |
| `orangepi-one-plus/` | H6 | `sun50i-h6-orangepi-one-plus.dtb` | `../uboot-orangepi-one-plus/u-boot-sunxi-with-spl.bin` @8 KiB | Orange Pi One Plus. |

Each table entry contains a full boot stack: `create-boot-script.sh` rebuilds
TF-A + U-Boot via `../build-uboot.sh`, copies the matching DTB into `/boot`,
the extlinux stanza points at it, and `genimage.cfg` injects the proper SPL
binary. To add another sun50i platform, clone the closest board directory,
adjust the DTB file name, set the new `UBOOT_DEFCONFIG` / `UBOOT_TARGET` in
the staging script, and update `genimage.cfg` to reference the matching
`../uboot-<target>/...` artifact.

---

## Shared Rootfs Overlay (`fsoverlay/`)

- `etc/asound.conf` switches the default ALSA device to a `dmix` stack on `hw:0,0`,
  giving software mixing across HDMI and analog codecs.
- `etc/modules.conf` preloads the audio and Wi-Fi kernel modules expected by
  H5/H6 boards.
- `usr/bin/install2emmc` flashes the generated image from SD to onboard eMMC.
- `usr/bin/{cpu,gpu}temp` and `usr/bin/hciattach_opi` expose temperature monitoring
  and BT bring-up helpers for panel UIs.
- `usr/share/alsa/cards/` contains mixer presets for analog/HDMI/SPDIF output.

Add per-board config files under this overlay to have them merged before the
image is packed.

---

## Package Patches (`patches/`)

- `mupen64plus-video-glide64mk2/mupen64plus-video-glide64mk2-aarch64-render.patch`
  removes inline x86 assembly and relies on portable 64-bit math.
- `ppsspp/002-force-gles20-lima.patch` forces PPSSPP to request a GLES 2.0 context
  and keeps the SDL window visible.
- `u-boot/0001-Libretech-H5-set-ddr3-to-744Mhz.patch` tunes DRAM for the Tritium H5.
- `u-boot/0001-OrangePi-3-LTS-support.patch` adds Orange Pi 3 LTS support.
- `u-boot/0002-Silence-uboot-serial-logs.patch` quiets U-Boot serial output.

Drop additional fixes as `patches/<package>/<description>.patch` and reference
them from the corresponding Buildroot package `.mk`.

---

## Trusted Firmware Patch Stack

`patches/arm-trusted-firmware/0001-sunxi-Don-t-enable-referenced-regulators.patch`
is applied by `build-uboot.sh` before TF-A is rebuilt. Keep this section updated
as you add new TF-A patches so contributors know why they exist.
