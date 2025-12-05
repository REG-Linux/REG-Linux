# REG-Linux · Allwinner H5 Boards

This folder hosts everything needed to build and customize REG-Linux images for Allwinner H5 devices (Orange Pi PC2, Libretech Tritium H5, etc.).
Each board directory ships the boot assets Buildroot expects, while common filesystem tweaks and package patches live alongside them.

---

## Quick Start

1. Select the board under `board/allwinner/h5/<board>/` inside your Buildroot/REG-Linux config.
2. Ensure the build uses:
   - `BR2_ROOTFS_OVERLAY="board/allwinner/h5/fsoverlay"`
   - `BR2_ROOTFS_POST_IMAGE_SCRIPT="board/allwinner/h5/<board>/create-boot-script.sh"`
3. Run your usual `make`. The post-image script stages kernel, initrd, DTB, and update bundles in `${REGLINUX_BINARIES_DIR}/boot`.
4. `genimage --config board/allwinner/h5/<board>/genimage.cfg` (automatically invoked by REG-Linux) emits `reglinux.img`, ready to flash with `dd` or `bmaptool`.

For rapid iteration, mount the generated `boot.vfat` and swap `/boot/linux` or `/boot/reglinux.update` without rebuilding the full image.

---

## Directory Map

| Path | Purpose |
| ---- | ------- |
| `fsoverlay/` | Root filesystem overlay applied to every H5 target. |
| `orangepi-pc2/` | Boot assets (extlinux, genimage, staging script) for Orange Pi PC2. |
| `tritium-h5/` | Same structure for Libretech Tritium H5 (ALL-H3-CC). |
| `build-uboot.sh` | Shared helper that downloads/patches U-Boot 2025.01, recompiles TF-A (`sun50i_a64`), and installs the SPL under `reglinux/uboot-<target>/`. |
| `patches/` | Package-specific fixes required by these boards. |

Each board directory contains:

| File | Description |
| ---- | ----------- |
| `boot/extlinux.conf` | Kernel entry pointing at `/boot/linux`, the DTB, and REG-Linux kernel args (`initrd=/boot/initrd.lz4 label=REGLINUX rootwait quiet splash console=ttyS0,115200`). |
| `create-boot-script.sh` | Post-image helper that first runs `../build-uboot.sh` to rebuild TF-A + U-Boot for the board, then copies kernel, initrd, squashfs, modules, firmware, rescue bundle, and the device tree into `${REGLINUX_BINARIES_DIR}/boot`. |
| `genimage.cfg` | Disk layout: 2 GiB FAT32 boot (`boot.vfat`), 256 MiB EXT4 userdata (`/userdata`), plus injection of the board’s U-Boot SPL at 8 KiB. Adjust sizes or SPL paths here when forking. |

---

## Board Reference

| Board dir | Device tree | U-Boot SPL path | Notes |
| --------- | ----------- | --------------- | ----- |
| `orangepi-pc2/` | `sun50i-h5-orangepi-pc2.dtb` | `../uboot-orangepi-pc2/u-boot-sunxi-with-spl.bin` | Works for Orange Pi PC2 SBCs. Drop extra firmware blobs into `BINARIES_DIR/firmware` so the staging script copies them automatically. |
| `tritium-h5/` | `sun50i-h5-libretech-all-h3-cc.dtb` | `../uboot-tritium-h5/u-boot-sunxi-with-spl.bin` | Covers Libretech Tritium H5 (ALL-H3-CC). Boot logic mirrors the PC2 layout; usually only the DTB/SPL path changes. |

To add another H5 platform, copy either directory, change the DTB reference, set the `UBOOT_DEFCONFIG`/`UBOOT_TARGET` variables in `create-boot-script.sh`, and update `genimage.cfg` to reference the matching `../uboot-<target>/u-boot-sunxi-with-spl.bin` directory.

---

## Shared Rootfs Overlay (`fsoverlay/`)

- `etc/asound.conf` switches the default ALSA device to a `dmix` stack on `hw:0,0`, giving software mixing across HDMI and analog codecs.
- `usr/bin/cputemp` / `usr/bin/gputemp` are lightweight shell scripts (from LibreELEC) that read `/sys/class/thermal/thermal_zone*/temp` and print Celsius values—handy for UI widgets or SSH diagnostics.
- `usr/share/alsa/cards/` contains mixer presets:
  - `H3_Audio_Codec.conf` unmutes the analog line-out path at boot.
  - `allwinner-hdmi.conf` and `allwinner-spdif.conf` set IEC958 mixer defaults for digital outputs.

Add any per-board config files under this overlay to have them merged before the image is packed.

---

## Package Patches (`patches/`)

- `mupen64plus-video-glide64mk2/mupen64plus-video-glide64mk2-aarch64-render.patch` removes inline x86 assembly and relies on portable 64-bit math, fixing GLES builds on aarch64.
- `ppsspp/002-force-gles20-lima.patch` forces PPSSPP to request an OpenGL ES 2.0 context and keeps the SDL window visible—matching the Lima driver’s stable path on H5 GPUs.

Drop additional fixes as `patches/<package>/<description>.patch` and reference them from the corresponding Buildroot package `.mk`.

---

Keep this README in sync with any new boards or overlays so future contributors can jump straight into the H5 build flow with minimal guesswork.
