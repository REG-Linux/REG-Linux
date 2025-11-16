# REG-Linux · Allwinner Boards

This folder collects the REG-Linux build assets for every Allwinner SoC family we support (H3, H5, H6, H616/H618, H700). Each subdirectory mimics the same Buildroot schema: a board-specific directory with `boot/extlinux.conf`, `create-boot-script.sh`, and `genimage.cfg`, plus sibling folders for shared overlays, patches, and kernel configs. Copy the nearest board directory when adding variants, tweak the DTB/SPL references, and keep the overlays/patch stacks aligned while doing so.

## Directory at a Glance

| Path | Description |
| ---- | ----------- |
| `h3/` | H2+/H3 Cortex-A7 boards (Banana Pi M2 Zero, Orange Pi variants, Capcom Home Arcade). |
| `h5/` | H5 SBCs (Orange Pi PC2, Libretech Tritium H5). |
| `h6/` | H6 SBCs (Orange Pi 3, Orange Pi 3 LTS, Orange Pi One Plus). |
| `h616/` | H616/H618 devices (Orange Pi Zero2 family, Banana Pi M4 Berry, X96 Mate). |
| `h700/` | Anbernic H700 handhelds (RG35XX/40XX series). |
| `linux_patches`, `patches/` | Shared patch collections referenced by multiple SoC folders. |

## H3 Family (`h3/`)

Quick start:

1. Set `reglinux-h3` as the target (`make h3-build`).
2. Buildroot merges `board/allwinner/h3/fsoverlay`, stages DTBs listed for the Orange Pi/Capcom boards, and points `BR2_GLOBAL_PATCH_DIR` to `board/allwinner/h3/patches`.
3. Post-image scripts copy `linux`, `initrd.lz4`, `reglinux.update`, overlays, and board-specific DTBs into `${REGLINUX_BINARIES_DIR}/boot`, where `genimage.cfg` arranges the partitions.

Highlights:

* Each board (Banana Pi M2 Zero, Capcom Home Arcade, Orange Pi One/PC/PC Plus/Plus2E) has its own layout plus a shared overlay that configures ALSA routing, temperature helpers, and Capcom-specific EmulationStation defaults.
* `patches/` keeps package tweaks such as forcing GLES2 for Lima-based PPSSPP builds.
* Refer to `configs/reglinux-h3.board`, the Linux fragment (`linux-sunxi32-current.config`), and the overlay list when adding new DTBs.

## H5 Family (`h5/`)

Quick start:

1. Point Buildroot at `board/allwinner/h5/<board>/`.
2. Use `h5/fsoverlay` and the board’s `create-boot-script.sh` for post-image work.
3. Run `make`; `genimage` (via `board/allwinner/h5/<board>/genimage.cfg`) produces `reglinux.img` with the U-Boot SPL placed at 8 KiB.

Highlights:

* Orange Pi PC2 and Libretech Tritium H5 share a ROOTFS overlay with ALSA mixer presets and temp helpers, plus `usr/bin/cputemp`, `gputemp`.
* Patches include collections for `mupen64plus-video-glide64mk2` (removing x86 asm) and `ppsspp` (forcing GLES2 contexts).
* Boot artifacts stage kernel, initrd, DTB, modules, firmware, rescue bundles, and firmware files listed under `BINARIES_DIR`.

## H6 Family (`h6/`)

Quick start:

1. Buildroot should select a target under `board/allwinner/h6/`.
2. Common helpers are `h6/fsoverlay` and the board’s `create-boot-script.sh`.
3. `genimage` uses each board’s `genimage.cfg` to inject the SPL at 8 KiB and pack boot/userdata partitions.

Highlights:

* Shared overlay provides `install2emmc`, temperature helpers, and boot module lists.
* ATF patches live under `patches/arm-trusted-firmware/`, currently keeping unused regulators disabled.
* Board entries cover Orange Pi 3, Orange Pi 3 LTS, and Orange Pi One Plus; each script stages the appropriate `.dtb` and SPL binary from `uboot-multiboard`.

## H616/H618 Family (`h616/`)

Quick start:

1. Select `board/allwinner/h616/<board>/` in your Buildroot config.
2. Use `h616/fsoverlay`, `create-boot-script.sh`, `genimage.cfg`, and let `build-uboot.sh` compile U-Boot 2025.01 for the selected board.
3. `genimage` assembles the 2 GiB boot and 256 MiB userdata partitions, injects the SPL, and populates `/boot` with REG-Linux payloads.

Highlights:

* The board list includes Banana Pi M4 Berry, Orange Pi Zero2/Zero2W/Zero3, and X96 Mate; each has a U-Boot defconfig pointing to `../uboot-<board>/u-boot-sunxi-with-spl.bin`.
* Kernel patches, DTBs, and overlay additions keep Wi-Fi, display, and periferal support in sync; `linux_patches/` and `dts/` supply out-of-tree kernels.
* Overlay installs modules for Cedrus VPU, Bluetooth UART, and ensures ALSA defaults are consistent.

## H700 Family (`h700/`)

Quick start:

1. Buildroot targets `board/allwinner/h700/anbernic-h700`.
2. Apply `h700/fsoverlay`, run `create-boot-script.sh`, and rely on `genimage.cfg` for the disk layout.
3. `build-uboot.sh` downloads U-Boot v2025.10, applies `patches/uboot-rg35xx`, and the script stages every handheld DTB into `${REGLINUX_BINARIES_DIR}/boot`.

Highlights:

* Single directory covers every RG35XX/RG40XX/RG34XX/RG28XX/RGCubeXX variant; the DTB table documents the name-to-device mapping.
* `dracut.conf` + `kernel-firmware.txt` pin the panel and RTL8821CS firmware injected into initramfs.
* `linux_patches/` and `reglinux_rg35xx_kernel_optimization.patch` keep the kernel lean, while `patches/mupen64plus-video-glide64mk2/` mirrors the GLES fix from other Allwinner trees.

Keep this README updated whenever you add new overlays, patches, or DTBs so contributors can orient themselves before diving into the per-board folders.
