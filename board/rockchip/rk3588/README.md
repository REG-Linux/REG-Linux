# Rockchip RK3588 Board Support

This directory holds the REG-Linux board support for Rockchip RK3588-based devices. Each subdirectory represents one of the downstream consumer boards we support; the shared resources describe the kernel configuration, kernel patches, firmware overlays, and helper scripts needed to assemble a working `reglinux.img` for flashing.

## Shared resources

- `linux-defconfig.config` – the flattened Linux kernel configuration (6.1.118, Buildroot 2025.02.7 toolchain). It enables `CONFIG_LOCALVERSION="-reglinux"`, `CONFIG_WERROR`, and all of the RK3588 drivers needed for REG-Linux. Use it as the base for the kernel that gets packaged into every board image.
- `linux_patches/` – a small series of kernel patches applied on top of that defconfig. They rename the CW2015 battery driver, silence new warning builds, add the Radxa wireless workaround, enable Panthor support, fix polling and power-off helpers, adjust CMA/Ion allocations, refine GameForce Ace input/audio, and tune UVC bandwidth among other board-specific tweaks.
- `patches/` – Buildroot/package patches that touch the userland tooling we ship. They include fixes for `moonlight-embedded`, SDL2/OpenGLES, RTL8821CU Wi-Fi, Vita3K, PPSSPP, XInput/xpad, and U-Boot patches that add the RK3588 HDMI node plus upstream fixes (see the `uboot/` subdirectory for the three patches applied before building U-Boot).
- `dts/` – contains `rk3588s-gameforce-ace.dts`, the custom device tree source used to build the GameForce Ace DTB referenced by that board’s `extlinux.conf`.
- `fsoverlay/` – a small rootfs overlay that injects runtime helpers: custom `inittab`, fan/audio init scripts, an `opts.9tripod_rk3588s_Board` option file, ALSA configuration, a `brcm_patchram_plus` binary for Bluetooth, and Mali firmware (`mali_csffw.bin`). Buildroot layers this on top of the target rootfs before packaging so the fan and audio workflows are available out of the box.
- `build-uboot.sh` – shared helper at the root of this directory. It takes the host dir, board dir, image staging dir, U-Boot defconfig, and target name, reuses a cached U-Boot tarball/rkbin clone, applies the patches in `patches/uboot`, and emits `u-boot-rockchip.bin` under `reglinux/uboot-<target>`.

## Boot image layout

Every board uses its own `create-boot-script.sh` and `genimage.cfg`: the script copies the kernel (`Image`), `initrd.lz4`, update bundles (`reglinux.update`, `modules.update`, `firmware.update`, `rescue.update`), and the board’s `extlinux.conf` into the staging tree under `REGLINUX_BINARIES_DIR`. Boards that build U-Boot invoke the shared `build-uboot.sh` helper (the Khadas Edge 2 flow is still disabled so it relies on an external bootloader). The helper reuses a cached U-Boot 2025.10 tarball and `rkbin` clone, applies the patches from `patches/uboot`, and produces `u-boot-rockchip.bin` inside `reglinux/uboot-<board>`.

`genimage.cfg` then generates `reglinux.img` with a 3 GiB FAT32 boot partition and a 256 MiB `userdata.ext4` partition labeled `SHARE`. The GPT image contains an `uboot` region that simply embeds the generated `u-boot-rockchip.bin`. `extlinux.conf` always points to `/boot/linux`, `/boot/initrd.lz4`, and the DTB under `/boot` while enabling `console=ttyS0,115200n8` and `coherent_pool=2M`.

## Supported boards

| Board | builds U-Boot in-tree? | Device tree loaded by `extlinux` | Notes |
| --- | --- | --- | --- |
| `bananapi-m7` | yes | `/boot/rk3588-bananapi-m7.dtb` | `build-uboot.sh` stages `uboot-bananapi-m7`. |
| `firefly-station-m3` | no (expects externally provided U-Boot) | `/boot/rk3588s-roc-pc.dtb` | relies on stock Rockchip RK3588 image; no local UB build script. |
| `gameforce-ace` | yes | `/boot/rk3588s-gameforce-ace.dtb` | the only board with a DTS source under `dts/`; `linux_patches` include GameForce Ace input/audio fixes. |
| `indiedroid-nova` | yes | `/boot/rk3588s-9tripod-linux.dtb` | standard RK3588 pipeline. |
| `khadas-edge-2` | no (Khadas-specific bootloader) | `/boot/rk3588s-khadas-edge2.dtb` | mainline U-Boot build is disabled because of the OOWOW MCU, so it relies on the upstream Khadas bootloader. |
| `mekotronics-r58` | no | `/boot/rk3588-blueberry-edge-v12-linux.dtb` | expects upstream U-Boot build. |
| `orangepi-5` | yes | `/boot/rk3588s-orangepi-5.dtb` | standard pipeline. |
| `orangepi-5b` | yes | `/boot/rk3588s-orangepi-5b.dtb` | standard pipeline. |
| `orangepi-5-plus` | yes | `/boot/rk3588-orangepi-5-plus.dtb` | standard pipeline. |
| `quartzpro64` | no | `/boot/rk3588-evb1-lp4-v10-linux.dtb` | expected to run with externally supplied U-Boot binary. |
| `rock-5a` | yes | `/boot/rk3588s-rock-5a.dtb` | standard pipeline. |
| `rock-5b` | yes | `/boot/rk3588-rock-5b.dtb` | standard pipeline. |
| `rock-5c` | yes | `/boot/rk3588s-rock-5c.dtb` | standard pipeline. |

Every board directory also bundles a `boot/extlinux.conf` that matches the DTB above and a `genimage.cfg` with the shared partition layout. The `create-boot-script.sh` files use the same argument ordering (`HOST_DIR`, `BOARD_DIR`, `BUILD_DIR`, `BINARIES_DIR`, `TARGET_DIR`, `REGLINUX_BINARIES_DIR`) so the Buildroot board package can call them uniformly.

## Extending this tree

1. To add a new board, copy one of the existing board directories and adjust `boot/extlinux.conf`, `genimage.cfg`, and optionally the DTB name. Have its `create-boot-script.sh` invoke the shared `build-uboot.sh` helper when a local U-Boot build is desired.
2. Update `linux_patches` when kernel fixes are required and list new userland fixes under `patches/` so the Buildroot system applies them automatically.
3. Drop additional files into `fsoverlay/` if you need more runtime helpers or firmware blobs.
4. Keep `linux-defconfig.config` in sync with the kernel flavor you want to ship; rebuild it via `make savedefconfig` from the kernel tree if you change options.

This layout keeps each RK3588 board’s boot configuration, kernel options, and packaging logic close together while sharing the overlay and patchwork that REG-Linux needs to behave consistently across devices.
