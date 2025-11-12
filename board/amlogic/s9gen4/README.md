# REG Linux · Amlogic S9 Gen4 (S905Y4 / Khadas VIM1S) Support Pack

This directory backs the `reglinux-s9gen4` Buildroot target (`make
s9gen4-build`). It contains the Khadas VIM1S boot assets, signed U-Boot
handling, dracut recipe, overlays, kernel config, and patch queues
needed to turn the generic Buildroot output into a drop-in image for the
S905Y4 (“Gen4”) platform.

---

## Directory Map

Path | Description
---- | -----------
`khadas-vim1s/` | Boot assets (`boot/`), post-image hook, `genimage.cfg`, and helper for copying the signed VIM1S U-Boot blob.
`fsoverlay/` | VIM1S-specific rootfs overlay (ALSAlib policy, Plymouth control, wifi + video firmware init scripts, module options).
`linux-vim1s-5.15.137.config` | Full kernel configuration sourced from Khadas’ 5.15 tree.
`linux-defconfig-fragment.config` | Extra fragment layered on top of the vendor defconfig.
`linux_patches/` | Patch set for the Khadas kernel tarball (audio clock fixes, fbdev verbosity tweaks, Bifrost updates, TEE TA fixes, hdmitx content-type forcing, etc.).
`patches/` | Buildroot package adjustments: Realtek out-of-tree drivers, SDL2 DRM fix, RetroArch Wayland patches, Vulkan loader revert, FBV splash fix, MangoHUD stats adjustments.
`dracut.conf` | Initramfs recipe that preloads Broadcom Wi‑Fi blobs, OP‑TEE firmware, and trims unused modules to keep the gzip’d initrd small.

---

## Board Highlights

Board dir | Device tree(s) | Notes
--------- | --------------- | -----
`khadas-vim1s/` | `kvim1s.dtb` | Post-image hook copies the signed `u-boot.bin.sd.signed` produced by `BR2_PACKAGE_UBOOT_VIM1S`, stages `Image`, `initrd.gz`, `reglinux.update`, `modules`, `firmware`, `rescue`, and the DTB under `boot/boot/`, then drops a Khadas-style `boot/extlinux.conf`. `genimage.cfg` injects the signed U-Boot blob at offset 0 (with the `(440;512)` gap) before laying out the VFAT boot and EXT4 userdata partitions.

---

## Overlay & Initramfs Notes

- `fsoverlay/etc/init.d/S002plymouth` keeps Plymouth’s splash disabled
  during boot/shutdown to avoid the HDMI glitches that happen on the
  VIM1S.
- `fsoverlay/etc/init.d/S03kvim-video-firmware` preloads OP‑TEE/TEE
  firmware and the video microcode so the GPU is ready when Sway starts.
- `fsoverlay/etc/init.d/S03kvim-fan` is kept for parity with VIM4, even
  though the VIM1S lacks an onboard fan by default—it is harmless and
  supports add-on cooling kits.
- ALSA configs (HDMI card + `alsa.conf`) ensure HDMI audio is the
  default sink while leaving I2S accessible.
- `dracut.conf` mirrors the A3 Gen2 recipe: it disables unnecessary
  modules, force-installs every Broadcom firmware blob, and keeps the
  initramfs gzip-compressed because the Khadas boot chain expects it.

---

## Build Integration

`configs/reglinux-s9gen4.board` does the following:

- Targets Cortex-A35 + musl, Panfrost/Vulkan, and enables SWAY +
  Xwayland.
- Pulls the Khadas vendor kernel tarball from
  `https://github.com/khadas/linux/archive/99ab673b...tar.gz`, applies
  `linux-vim1s-5.15.137.config`, and merges the fragments listed above.
- Applies the `linux_patches/` queue for mesa/Bifrost fixes, HDMI color
  tweaks, GCC13 compatibility, etc.
- Requests DTB support for `kvim1s`.
- Configures `BR2_TARGET_ROOTFS_CPIO_DRACUT_CONF_FILES` to point at this
  folder’s `dracut.conf` and keeps the initrd gzip’d.
- Enables `BR2_PACKAGE_UBOOT_VIM1S` so the signed `u-boot.bin.sd.signed`
  lands in `images/uboot-vim1s/`, ready for `create-boot-script.sh` and
  `genimage`.

Build command:

```bash
make s9gen4-build
```

Images are emitted to
`output/s9gen4/images/reglinux/images/khadas-vim1s/`.

---

## Boot & Image Layout

- `create-boot-script.sh` copies the prebuilt U-Boot blob into
  `build-uboot-vim1s/`, stages the kernel (`Image`), initrd.gz,
  SquashFS update set, modules, firmware, rescue bundle, and `kvim1s.dtb`
  into `boot/boot/`, then installs `boot/extlinux.conf`.
- `genimage.cfg` writes the signed Khadas U-Boot at LBA0 (leaving the MBR
  gap untouched), creates a 2 GiB FAT boot partition, and appends a
  256 MiB `SHARE` EXT4 userdata partition.
- The resulting SD image boots exactly like Khadas’ stock firmware, so
  vendor instructions for reflashing still apply.

---

## Extending S9 Gen4 Support

1. Clone `khadas-vim1s/` for the next board, adjust the staged DTB(s)
   inside `create-boot-script.sh`, and edit `boot/extlinux.conf` with
   the correct serial console + arguments.
2. Update `configs/reglinux-s9gen4.board` with the extra DTB and any
  kernel fragment changes you require.
3. Drop board-specific firmware or init scripts into `fsoverlay/` and
  extend `dracut.conf` if the initramfs must carry extra blobs.
4. Keep additional kernel/package patches inside `linux_patches/` and
  `patches/` so they are version-controlled with the rest of the
  support pack.

Please reflect new hardware here so S905Y4 contributors understand the
boot flow and where to place their changes. 
