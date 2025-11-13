# REG Linux · Amlogic S905 Gen3 (SM1/S905X3) Support Pack

`board/amlogic/s905gen3/` feeds the `reglinux-s905gen3` Buildroot
target (`make s905gen3-build`). It bundles everything required to ship
images for the SM1-based generation: Banana Pi M5, Khadas VIM3L,
Odroid-C4, and the generic “S905X3 TV box” image that targets common
H96/X96/A95X clones. This includes the boot assets, U-Boot build helpers,
per-board DTBs, overlays, and patch queues.

---

## Directory Map

Path | Description
---- | -----------
`bananapi-m5/`, `khadas-vim3l/`, `odroid-c4/`, `s905x3-tvbox/` | Per-board boot directories with `boot/`, `create-boot-script.sh`, `genimage.cfg`, and optional `build-uboot.sh`.
`fsoverlay/` | Keeps the HDMI ALSA card config aligned with other Amlogic boards.
`linux-defconfig-fragment.config` | Adds SM1-specific Kconfig bits on top of the shared Meson64 defconfig.
`linux_patches/` | Enables the X96 Max Plus DTBs (100M + 2101 revisions) that upstream doesn’t ship yet.
`patches/uboot/` | Shared Meson64 U-Boot tweaks applied to every mainline build (stdout on UART, sane `fdtdir`, etc.).

---

## Board Highlights

Board dir | Device tree(s) | Notes
--------- | --------------- | -----
`bananapi-m5/` | `meson-sm1-bananapi-m5.dtb` | Builds U-Boot 2025.01 (`bananapi-m5_defconfig`) with the local patches, stages extlinux + standard REG Linux boot payload.
`khadas-vim3l/` | `meson-sm1-khadas-vim3l.dtb` | Chain-loads mainline U-Boot via the vendor scripts still present on eMMC. Copies `boot.ini`, `boot.scr`, and every AML script, then writes `u-boot.bin` as `u-boot.bin` so the vendor BL2/BL30 can find it.
`odroid-c4/` | `meson-sm1-odroid-c4.dtb` | Mainline U-Boot (2025.01 `odroid-c4_defconfig`) with LibreELEC’s FIP packaging; standard extlinux boot.
`s905x3-tvbox/` | `meson-sm1-h96-max.dtb`, `meson-sm1-sei610.dtb`, `meson-sm1-khadas-vim3l.dtb`, `meson-sm1-odroid-c4.dtb`, `meson-sm1-x96-air*.dtb`, `meson-sm1-a95xf3-air*.dtb`, `meson-sm1-x96-max-plus*.dtb` | Generic TV box image. Copies a bundle of DTBs, keeps the kernel as `Image` + `uInitrd`, installs `boot.ini`, `uEnv.txt`, and generates AML/S905 `mkimage` scripts so users only need to edit `uEnv.txt` when switching boxes.

---

## Overlay & Patch Notes

- `fsoverlay/usr/share/alsa/cards/HDMI.conf` ensures HDMI is the default
  ALSA sink; drop per-board configs here if needed.
- `linux_patches/00{1,2}-enable-x96...` simply wire up the downstream DT
  files for the X96 Max Plus variants until they land upstream.
- `patches/uboot/*.patch` matches the sets used on other Amlogic packs,
  ensuring `fdtdir /boot/boot` works and HDMI logging stays disabled.

---

## Build Integration

From `configs/reglinux-s905gen3.board`:

- Cortex-A55/glibc toolchain with `BR2_PACKAGE_SYSTEM_PANFROST_MESA3D`
  and SWAY Wayland enabled.
- Uses the upstream Meson64 defconfig
  (`board/amlogic/linux-meson64-current.config`), the shared REG Linux
  fragment, plus `linux-defconfig-fragment.config` for SM1-specific
  toggles (USB3, eMMC HS200, etc.).
- Applies the shared Amlogic kernel patch queue plus the local SM1
  `linux_patches/`.
- Enables `BR2_PACKAGE_HOST_MESON_TOOLS` so the build can pack BL2/BL31
  blobs when the post-image hook needs them.
- Rootfs: SquashFS (Zstd) + LZ4 initramfs; also produces a `uInitrd`
  because the TV-box image expects that format.

Build command:

```bash
make s905gen3-build
```

Resulting artifacts sit under
`output/s905gen3/images/reglinux/images/<board>/`.

---

## Boot & Image Layout

- Board-specific `create-boot-script.sh` helpers stage the kernel,
  `initrd.lz4` (or `uInitrd` for TV boxes), `reglinux.update`, `modules`,
  `firmware`, `rescue`, and the DTBs into `boot/boot/`, then copy the
  matching `boot/extlinux.conf` (or `uEnv.txt`/`boot.ini` for TV boxes).
- `build-uboot.sh` scripts fetch U-Boot 2025.01, apply the shared patch
  set, build the proper defconfig, then run LibreELEC’s
  `amlogic-boot-fip` helper so SPI/eMMC flashing works.
- `s905x3-tvbox/create-boot-script.sh` skips extlinux entirely—users
  pick DTBs via `uEnv.txt`. It also copies a gzipped `boot-logo.bmp` and
  generates AML + `boot.scr` scripts via `mkimage`.

---

## Extending S905 Gen3 Support

1. Duplicate the closest board folder, update the DTB name inside
   `create-boot-script.sh`, and adjust serial console / video params in
   the boot config file.
2. Add the DTB to
   `BR2_LINUX_KERNEL_INTREE_DTS_NAME` inside
   `configs/reglinux-s905gen3.board`.
3. Extend `linux-defconfig-fragment.config` or add patches if the new
   hardware needs additional drivers/quirks.
4. Place any board-specific firmware or ALSA/udev tweaks under
   `fsoverlay/`.

Document those additions here so the SM1/X3 matrix stays navigable. 
