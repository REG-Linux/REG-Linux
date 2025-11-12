# REG-Linux · Allwinner H700 (RG35XX/RG40XX) Boards

This folder holds the REG-Linux build assets for every Anbernic handheld that uses the Allwinner H700 SoC (RG35XX 2024/H/Plus/SP/Pro, RG40XX H/V, RG34XX, RG28XX, RGCubeXX, etc.).
The layout mirrors other SoC families but adds a few extras (panel firmware list, dracut profile, large kernel patch stack) needed to boot these handhelds cleanly.

---

## Quick Start

1. Point Buildroot at `board/allwinner/h700/anbernic-h700` (all H700 handhelds share the same directory).
2. Configure the common helpers:
   - `BR2_ROOTFS_OVERLAY="board/allwinner/h700/fsoverlay"`
   - `BR2_ROOTFS_POST_IMAGE_SCRIPT="board/allwinner/h700/anbernic-h700/create-boot-script.sh"`
3. Run `make`. The post-image script will:
   - invoke `build-uboot.sh` (downloads U-Boot v2025.10, applies `patches/uboot-rg35xx/*.patch`, builds `anbernic_rg35xx_h700_defconfig`, and stores `u-boot-sunxi-with-spl.bin` under `${REGLINUX_BINARIES_DIR}/uboot-anbernic-rg35xx/`);
   - copy the kernel, initrd, squashfs update, modules, firmware, rescue bundle, and **every** DTB variant listed below into `${REGLINUX_BINARIES_DIR}/boot`;
   - stage `boot/extlinux.conf` pointing to the RG35XX Plus DTB by default.
4. `genimage --config board/allwinner/h700/anbernic-h700/genimage.cfg` emits `reglinux.img` with the SPL injected at 8 KiB, a 2 GiB FAT32 boot partition, and a 256 MiB userdata EXT4.

Switching hardware variants only requires editing `boot/extlinux.conf` (or copying the matching DTB name into the `FDT` line) before flashing.

---

## Directory Map

| Path | Purpose |
| ---- | ------- |
| `anbernic-h700/boot/` | Extlinux stanza plus all DTBs the handheld family needs. |
| `anbernic-h700/build-uboot.sh` | Fetches U-Boot v2025.10, applies RG35XX-specific patches, builds `anbernic_rg35xx_h700_defconfig`, and exports the SPL. |
| `anbernic-h700/create-boot-script.sh` | Post-image helper that runs the U-Boot builder and stages `/boot`. |
| `anbernic-h700/genimage.cfg` | Disk layout (SPL offset, boot/userdata partitions). |
| `dracut.conf` | Custom dracut profile that strips systemd and kernel-modules from the initramfs to keep it small on handhelds; also forces panel and Wi-Fi firmware into the image. |
| `kernel-firmware.txt` | Firmware whitelist consumed by the kernel package to make sure panel blobs and RTL8821CS files land in `/lib/firmware`. |
| `fsoverlay/` | Shared rootfs overlay (modules.conf plus helper scripts such as `enable-bluetooth.sh`, `cputemp`, `gputemp`, `hciattach_opi`). |
| `linux_patches/` | Kernel patch queue enabling DE33 display, new panel drivers, joystick/input devices, PWM backlight, OTG fixes, etc. |
| `reglinux_rg35xx_kernel_optimization.patch` | Delta applied to `linux-sunxi64-current.config` to keep the handheld kernel lean (disables audit, shrinks printk buffers, etc.). |
| `patches/uboot-rg35xx/` | Applied by `build-uboot.sh` before compiling U-Boot. |
| `patches/mupen64plus-video-glide64mk2/` | Userland GLES compatibility fix shared with other Allwinner families. |

---

## Board & DTB Reference

All hardware variants are covered by the single `anbernic-h700/` directory. The table below lists the DTB names copied into `/boot` and the device each one targets:

| DTB file | Devices |
| -------- | ------- |
| `sun50i-h700-anbernic-rg35xx-2024.dtb` | RG35XX 2024 refresh (13:9 panel). |
| `sun50i-h700-anbernic-rg35xx-2024-rev6-panel.dtb` | RG35XX 2024 units with the Rev6 LCD panel. |
| `sun50i-h700-anbernic-rg35xx-h.dtb` | RG35XX H. |
| `sun50i-h700-anbernic-rg35xx-h-rev6-panel.dtb` | RG35XX H Rev6 LCD. |
| `sun50i-h700-anbernic-rg35xx-plus.dtb` | RG35XX Plus (default selection in `extlinux.conf`). |
| `sun50i-h700-anbernic-rg35xx-plus-rev6-panel.dtb` | RG35XX Plus Rev6 LCD. |
| `sun50i-h700-anbernic-rg35xx-sp.dtb` | RG35XX SP. |
| `sun50i-h700-anbernic-rg35xx-sp-v2-panel.dtb` | RG35XX SP v2 panel variant. |
| `sun50i-h700-anbernic-rg35xx-pro.dtb` | RG35XX Pro. |
| `sun50i-h700-anbernic-rg40xx-h.dtb` | RG40XX H. |
| `sun50i-h700-anbernic-rg40xx-v.dtb` | RG40XX V. |
| `sun50i-h700-anbernic-rg34xx.dtb` | RG34XX. |
| `sun50i-h700-anbernic-rg34xx-sp.dtb` | RG34XX SP. |
| `sun50i-h700-anbernic-rg28xx.dtb` | RG28XX. |
| `sun50i-h700-anbernic-rgcubexx.dtb` | RGCubeXX. |

All DTBs share the same boot assets; only the `FDT` line in `boot/extlinux.conf` must change when flashing a different handheld.

---

### Kernel & Initrd Notes

- `linux_patches/0001…0204` enable the DE33 display engine, HDMI audio, PWM backlight, RGB LEDs, VPU/GPU OPP tables, UWE5622 BT/Wi-Fi, and the various panel drivers these handhelds require.
- `reglinux_rg35xx_kernel_optimization.patch` is a trimmed-down config diff applied after Buildroot generates `linux-sunxi64-current.config`. Keep it in sync with any new config options you need.
- `dracut.conf` explicitly adds the RTL8821CS and panel firmware listed in `kernel-firmware.txt` to prevent boot-time surprises when the initrd is regenerated outside of Buildroot.

Whenever you add a new variant (panel, RAM SKU, etc.), copy the matching DTB into `boot/`, update the table above, and make sure `create-boot-script.sh` stages it so the flashing instructions stay accurate.
