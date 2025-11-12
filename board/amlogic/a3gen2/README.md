# REG Linux · Amlogic A3 Gen2 (A311D2) Support Pack

Everything under `board/amlogic/a3gen2/` is pulled in by the
`reglinux-a3gen2` Buildroot target (`make a3gen2-build`). This pack
contains the boot assets, Khadas-provided kernel tree, initramfs
customizations, and patches that transform the generic Buildroot output
into a drop-in image for the Khadas VIM4 (A311D2 “A3 Gen2”) family.

---

## Directory Map

Path | Description
---- | -----------
`khadas-vim4/` | Boot script, extlinux entry, image recipe, and helper that copies the signed VIM4 U-Boot blob out of `uboot-vim4/`.
`fsoverlay/` | A311D2-specific rootfs overlay (fan controller, OP‑TEE video firmware preload helpers, ALSA policy, Realtek Wi‑Fi module defaults).
`linux-kvim4-5.15.137.config` | Full kernel configuration from Khadas’ 5.15 vendor tree.
`linux-defconfig-fragment.config` | Extra Kconfig fragment layered on top of the vendor defconfig (Wayland bits, DRM fixes, etc.).
`linux_patches/` | Patch queue for the Khadas kernel tarball (Bifrost fixes, fbdev/logging tweaks, GCC13 fixes, ISP disablement, etc.).
`patches/` | Buildroot package tweaks: Realtek out-of-tree drivers, SDL2 KMS/DRM fix, Vulkan loader revert, RetroArch/MangoHUD Wayland stability, and FBV splash fixes.
`dracut.conf` | Custom dracut recipe that seeds all Broadcom/AMlogic firmware, OP‑TEE blobs, and disables unused initramfs modules so the compressed initrd stays tiny.

Each board directory (`khadas-vim4/` today) ships the usual REG Linux
boot trio: `create-boot-script.sh`, `boot/extlinux.conf`, and
`genimage.cfg`. Use it as the baseline if another A311D2 board is added.

---

## Board Highlights

Board dir | Device tree(s) | Notes
--------- | --------------- | -----
`khadas-vim4/` | `kvim4.dtb`, `kvim4n.dtb` | Wraps the Khadas signed U‑Boot (`u-boot.bin.sd.signed`) that comes from the `BR2_PACKAGE_UBOOT_VIM4` build. The post-image hook stages both DTBs under `/boot/boot/amlogic/` and drops an extlinux entry that uses `FDTDIR /boot/` so switching between VIM4/VIM4-N only requires renaming the DTB. Kernel/initrd stay gzip-compressed to match the vendor boot chain.

---

## Filesystem Overlay & Initramfs

- `fsoverlay/etc/init.d/S03kvim-video-firmware` preloads OP‑TEE and the
  Khadas VPU firmware before the UI starts, avoiding first-frame stalls.
- `fsoverlay/etc/init.d/S03kvim-fan` raises the automatic fan trip
  points (60/70/80 °C) and flips the fan into automatic mode during
  boot.
- `fsoverlay/etc/init.d/S002plymouth` keeps Plymouth in text-only mode,
  preventing the HDMI handshake lockups seen with the vendor splash.
- ALSA cards/config files point `default` at HDMI while keeping the
  analog codec unmuted.
- `dracut.conf` replaces the default initramfs feature set with a slim
  BusyBox-only build, blacklists unused storage/network modules, and
  force-installs every Broadcom Wi‑Fi calibration/NVRAM blob so the
  signed Khadas kernel has everything it expects at early boot.

---

## Build Integration

`configs/reglinux-a3gen2.board` wires this tree into Buildroot:

- Enables `BR2_PACKAGE_SYSTEM_TARGET_A3GEN2` (A73/A53 big.LITTLE) and
  hooks the shared overlays via
  `BR2_ROOTFS_OVERLAY="board/fsoverlay board/amlogic/fsoverlay board/amlogic/a3gen2/fsoverlay"`.
- Pulls the Khadas vendor kernel from
  `https://github.com/khadas/linux/archive/99ab673b...tar.gz`, applies
  `linux_kvim4-5.15.137.config`, and stacks the local fragments +
  `board/reglinux/linux-defconfig-reglinux.config`.
- Points `BR2_LINUX_KERNEL_DTS_SUPPORT` at `kvim4`/`kvim4n` and applies
  the patches under `board/amlogic/a3gen2/linux_patches`.
- Requests the dracut recipe in this folder and keeps the initrd gzip’d
  (`BR2_TARGET_ROOTFS_CPIO_GZIP=y`) to match the vendor signing tools.
- Enables the Mesa Panfrost+Vulkan stack and Xwayland so the Mali-G610
  GPU exposes both modern Wayland and legacy GLX paths.
- Uses the packaged `UBOOT_VIM4` binary instead of rebuilding U-Boot in
  tree; the post-image hook simply copies the signed blob into the
  `genimage` workspace.

Typical build flow:

```bash
make a3gen2-build
```

Artifacts land under `output/a3gen2/images/reglinux/images/khadas-vim4/`.

---

## Boot & Image Layout

- `create-boot-script.sh` runs after `fs/` is populated. It copies the
  signed U-Boot into `build-uboot-vim4/`, stages `Image`, `initrd.gz`,
  SquashFS updates (`reglinux.update`, `modules.update`, etc.), all
  firmware bundles, and both DTBs under `boot/boot/amlogic/`.
- `boot/extlinux.conf` keeps the Khadas `bootargs` placeholders so users
  can still override settings from SPI/eMMC U-Boot.
- `genimage.cfg` embeds the signed U-Boot as an MBR-less blob at offset
  0 with the required `(440;512)` gap, then lays out a 2 GiB VFAT boot
  partition followed by a 256 MiB `SHARE` EXT4 userdata slice.

---

## Extending A3 Gen2 Support

1. Copy `khadas-vim4/` to a new board directory and update:
   - The DTB(s) staged inside `create-boot-script.sh`.
   - Serial console arguments / labels inside `boot/extlinux.conf`.
   - Partition sizes inside `genimage.cfg` if the target needs a
     different boot/userdata split or custom bootloader blob.
2. Add any new firmware, init scripts, or ALSA routes to
   `fsoverlay/` and extend `dracut.conf` if the initrd must carry extra
   blobs.
3. Reference the new board inside `configs/reglinux-a3gen2.board`
   (DTB list, overlays, additional kernel fragments) and commit any
   kernel or package patches alongside the existing queues.

Keeping this README updated when you touch the overlay, kernel patches,
or board scripts makes it much easier for others to iterate on VIM4
support without reverse-engineering the tree. 
