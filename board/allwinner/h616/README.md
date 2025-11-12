# REG-Linux · Allwinner H616/H618 Boards

This tree contains everything required to build REG-Linux images for Allwinner H616/H618 based devices (Orange Pi Zero family, Banana Pi M4 Berry, X96 Mate, etc.).
Every board directory ships the boot assets Buildroot expects, while the top-level helpers provide the kernel, DT, and filesystem customizations shared between targets.

---

## Quick Start

1. Select the target under `board/allwinner/h616/<board>/` inside your Buildroot configuration.
2. Apply the common settings:
   - `BR2_ROOTFS_OVERLAY="board/allwinner/h616/fsoverlay"`
   - `BR2_ROOTFS_POST_IMAGE_SCRIPT="board/allwinner/h616/<board>/create-boot-script.sh"`
3. Run `make`. The post-image script will:
   - spawn `build-uboot.sh` for the chosen board (downloads U-Boot v2025.01 from ftp.denx.de, applies `patches/u-boot/*.patch`, builds with `BL31=${BINARIES_DIR}/bl31.bin`, and drops the SPL into `REGLINUX_BINARIES_DIR/uboot-<board>/`);
   - stage the kernel, initrd, squashfs update, modules, firmware, rescue archive, DTB, and extlinux entry into `${REGLINUX_BINARIES_DIR}/boot`.
4. `genimage --config board/allwinner/h616/<board>/genimage.cfg` (automatically triggered by REG-Linux) packs `reglinux.img` with the SPL, a 2 GiB FAT32 boot partition, and a 256 MiB userdata EXT4.

If you need to iterate on the bootloader without rebuilding the whole image, reuse the generated `build-uboot-<board>/` directory, rebuild `u-boot-sunxi-with-spl.bin`, and rerun `genimage`.

---

## Directory Map

| Path | Purpose |
| ---- | ------- |
| `dts/` | Out-of-tree device trees that are copied into the kernel tree before it builds (e.g., Banana Pi M4 Berry, MangoPi MQ-Quad). |
| `fsoverlay/` | Files merged into every rootfs (modules.conf, helper scripts, Bluetooth bring-up). |
| `linux_patches/` | Large kernel patch stack enabling UWE5622 Wi-Fi/BT, DE33 display pipeline, HDMI audio, GPU/VPU nodes, etc. |
| `linux-sunxi64-current.config` | Baseline kernel configuration shared across all H616/H618 boards. |
| `patches/u-boot/` | Patches applied by every `build-uboot.sh` invocation. |
| `patches/mupen64plus-video-glide64mk2/` | Userland patch carried for GLES compatibility. |
| `<board>/boot/` | Extlinux stanza (and optional boot scripts) for that target. |
| `<board>/build-uboot.sh` | Fetches, patches, and compiles U-Boot v2025.01 for the board’s defconfig. |
| `<board>/create-boot-script.sh` | Post-image helper that calls the U-Boot build and stages `/boot`. |
| `<board>/genimage.cfg` | Disk image description (partition sizes plus SPL offset/path). |

---

## Board Reference

| Board dir | Device(s) | Device tree staged to `/boot` | U-Boot defconfig → SPL path | Notes |
| --------- | ---------- | ----------------------------- | --------------------------- | ----- |
| `bananapi-m4-berry/` | Banana Pi M4 Berry (H618) | `sun50i-h618-bananapi-m4berry.dtb` | `bananapi_m4_berry_defconfig` → `../uboot-bananapi-m4-berry/u-boot-sunxi-with-spl.bin` | Build script drops artifacts into `build-uboot-bananapi-m4-berry/` before the post-image step stages `/boot`. |
| `orangepi-zero2/` | Orange Pi Zero2 (H616) | `sun50i-h616-orangepi-zero2.dtb` | `orangepi_zero2_defconfig` → `../uboot-orangepi-zero2/u-boot-sunxi-with-spl.bin` | Use when targeting the H616 quad-core Zero2; expansion board USB nodes are enabled via kernel patches. |
| `orangepi-zero2w/` | Orange Pi Zero2W (H618) | `sun50i-h618-orangepi-zero2w.dtb` | `orangepi_zero2w_defconfig` → `../uboot-orangepi-zero2w/u-boot-sunxi-with-spl.bin` | Includes extra DTS fragments for on-board Wi-Fi/BT and PMU differences. |
| `orangepi-zero3/` | Orange Pi Zero3 (H618) | `sun50i-h618-orangepi-zero3.dtb` | `orangepi_zero3_defconfig` → `../uboot-orangepi-zero3/u-boot-sunxi-with-spl.bin` | GPU/VPU nodes and HDMI are enabled via `linux_patches/`. |
| `x96-mate/` | X96 Mate (H616 STB) | `sun50i-h616-x96-mate.dtb` | `x96_mate_defconfig` → `../uboot-x96-mate/u-boot-sunxi-with-spl.bin` | Ships both `extlinux.conf` and `boot/boot.scr` so boards that still read a legacy boot script will start the same kernel. |

All directories share the same disk geometry (2 GiB boot FAT, 256 MiB userdata) and copy the REG-Linux payloads (`linux`, `initrd.lz4`, `reglinux.update`, `modules.update`, `firmware.update`, `rescue.update`) into `/boot`. If you fork a board to support a new carrier or panel, ensure you update:

1. The DTB file name inside `create-boot-script.sh` and `boot/extlinux.conf`.
2. The SPL path and U-Boot defconfig inside `genimage.cfg` / `build-uboot.sh`.

---

### Kernel & Rootfs Customizations

- `linux_patches/0000-0018...` is the wifi/bt display patch series for the UWE5622 combo chip and DE33 display block; keep it in sync with the kernel version referenced by `linux-sunxi64-current.config`.
- `dts/*.dts` gets copied before the kernel build so you can maintain device-specific DTs out-of-tree.
- `fsoverlay/etc/modules.conf` and helper scripts provide a consistent module autoload list (Cedrus VPU, BT UART, etc.) across every H616/H618 build.

Document any additional overlays or patches you add here so future contributors know what the folder is meant to tweak.
