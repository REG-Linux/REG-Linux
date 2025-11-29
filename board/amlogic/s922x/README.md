# REG Linux · Amlogic S922X/A311D Support Pack

This directory feeds the `reglinux-s922x` Buildroot target (`make
s922x-build`). It contains everything required to produce REG Linux
images for the big A73/A53 Meson-G12B generation: Khadas VIM3,
Banana Pi M2S, Radxa Zero 2/Pro, Beelink GT-King (Pro), Odroid N2/N2+/N2L,
and the Odroid Go Ultra handheld.

---

## Directory Map

Path | Description
---- | -----------
`bananapi-m2s/`, `beelink-gtking/`, `beelink-gtking-pro/`, `khadas-vim3/`, `odroid-n2/`, `odroid-n2plus/`, `odroid-n2l/`, `radxa-zero2pro/` | Per-board boot directories with `boot/`, `create-boot-script.sh`, and `genimage.cfg`; they all reuse the shared `build-uboot.sh` helper under `board/amlogic/s922x/` (Odroid Go Ultra keeps its own flow).
`fsoverlay/` | Shared overlay: HDMI ALSA defaults, Realtek 8188eu blacklist, and `S02overclock` init script for the overclockable boards.
`linux-defconfig.config` | Base kernel configuration for this SoC family.
`linux_patches/` | Large patch queue (joypad drivers, OGU panel/battery stack, Beelink quirks, overclocking OPPs, RK818 regulators, uvc fixes, etc.).
`patches/uboot/` | Meson64 U-Boot patch set applied to every 2024.01 build (stdout on UART, `fdtdir` fixes, USB/NVMe boot order, MDIO mux).
`patches/uboot-ogu/` | Extra U-Boot patches required by the Odroid Go Ultra fork.

---

## Board Highlights

Board dir | Device tree(s) | Notes
--------- | --------------- | -----
`bananapi-m2s/` | `meson-g12b-a311d-bananapi-m2s.dtb` | Builds U-Boot 2024.01 (`bananapi-m2s_defconfig`), stages extlinux, and copies the DTB under `boot/boot/`.
`beelink-gtking/` | `meson-g12b-gtking.dtb` | Mainline U-Boot with the standard patch set; boots via extlinux.
`beelink-gtking-pro/` | `meson-g12b-gtking-pro.dtb` | Same as GT-King but with the Pro DTB and PSU quirks handled in `linux_patches/`.
`khadas-vim3/` | `meson-g12b-a311d-khadas-vim3.dtb` | U-Boot 2024.01 + LibreELEC FIP; standard extlinux boot, matching the VIM3 vendor layout.
`odroid-n2/` | `meson-g12b-odroid-n2.dtb` | Builds the Odroid N2 defconfig, drops both `boot.ini` and extlinux entries so the user can choose either boot method.
`odroid-n2plus/` | `meson-g12b-odroid-n2-plus.dtb` | Similar to the N2 build but stages the N2+ DTB and copies `boot.ini` into the VFAT partition.
`odroid-n2l/` | `meson-g12b-odroid-n2l.dtb` | Builds U-Boot 2024.01 with the shared helper (plus `odroid-n2l/patches/uboot/0001-add-bootcommand.patch` so the defconfig retries distro boot) before wrapping the kernel with `mkimage` and shipping `boot.ini`, `config.ini`, and a gzipped splash.
`odroid-go-ultra/` | `meson-g12b-odroid-go-ultra.dtb` | Special handheld target: copies `boot.ini`, uses the handheld-specific U-Boot patches in `patches/uboot-ogu`, stages `ODROIDBIOS.BIN` + the `res/` folder for the recovery UI, and keeps the initrd in `uInitrd` format.
`radxa-zero2pro/` | `meson-g12b-radxa-zero2.dtb` | Builds U-Boot 2024.01 (`radxa-zero2_defconfig`) with the shared patches, then stages extlinux + DTB.

All board helpers stage `Image`, `initrd.lz4`, `reglinux.update`,
`modules.update`, `firmware.update`, and `rescue.update` into
`boot/boot/` before copying the board-specific boot config.

---

## Overlay & Patch Highlights

- `fsoverlay/etc/init.d/S02overclock` reads `/boot/system-boot.conf` and
  raises CPU OPPs on the Odroid N2+/Beelink GT-King Pro/Khadas VIM3
  depending on the requested mode (default/high/extreme). It also
  disables the LITTLE cores for stability when overclocking.
- `fsoverlay/etc/modprobe.d/8188eu.conf` blacklists the obsolete 8188eu
  module—users rely on the out-of-tree variant shipped elsewhere in
  REG Linux.
- `linux_patches/` adds everything missing upstream: Odroid Go Ultra
  DSI panel and joypad driver, RK818 charger/battery stack, additional
  GPU OPPs, Beelink overclocking, USB HID quirks, and the `uvc`
  bandwidth cap needed for the Sinden light gun.
- `patches/uboot-ogu` updates Hardkernel’s OGU fork so it understands
  6.x kernels and boots from SD/eMMC with the new partition naming.

---

## Build Integration

Key points from `configs/reglinux-s922x.board`:

- Targets Cortex-A73+A53 (`BR2_cortex_a73_a53`), glibc, and enables the
  Panfrost Mesa stack plus REG Linux Vulkan/Xwayland options.
- Uses `linux-defconfig.config` + the shared REG Linux fragment +
  `linux_patches/` for Odroid/Beelink fixes.
- Builds DTBs for every supported board via
  `BR2_LINUX_KERNEL_INTREE_DTS_NAME`.
- Enables Wayland (SWAY) and Xwayland to cover both modern launchers and
  legacy X11 apps.
- Pulls in `BR2_PACKAGE_HOST_MESON_TOOLS` so the post-image scripts can
  repack BL2/BL30/BL31 when needed.
- Compresses the initramfs with LZ4 and the root SquashFS with Zstd.

Invoke:

```bash
make s922x-build
```

Artifacts live under
`output/s922x/images/reglinux/images/<board>/`.

---

## Boot & Image Layout

- Each board’s `create-boot-script.sh` copies the boot payload into
  `${REGLINUX_BINARIES_DIR}/boot/boot/`, drops either an extlinux entry
  or `boot.ini`/`uEnv.txt`, and now drives the shared
  `board/amlogic/s922x/build-uboot.sh` helper to rebuild the U-Boot
  payloads next to the rest of the staged binaries.
- The helper caches the U-Boot tarball and LibreELEC `amlogic-boot-fip`
  repo under `${REGLINUX_BINARIES_DIR}/build-uboot-cache/`, builds a
  clean copy of 2024.01, applies `patches/uboot/*.patch` (plus any
  `BOARD_DIR/patches/uboot/*.patch`, e.g.
  `odroid-n2l/patches/uboot/0001-add-bootcommand.patch`), and runs
  `./build-fip.sh` so every `uboot-<target>/` tree lives next to the
  assembled boot files.
- `odroid-go-ultra/create-boot-script.sh` still copies the `res/` assets
  and `ODROIDBIOS.BIN` that Hardkernel expects in recovery mode and uses
  the handheld-specific `patches/uboot-ogu` flow because it ships a
  bespoke U-Boot fork.
- `genimage.cfg` files follow the standard 2 GiB boot + 256 MiB userdata
  layout, with some boards (VIM3, Odroid Go Ultra) inserting a bootloader
  blob at offset 0.

---

## Extending S922X Support

1. Duplicate the closest board directory, update the DTB references in
   `create-boot-script.sh`, and adjust kernel args / serial consoles in
   the boot config.
2. Add the DTB to
   `BR2_LINUX_KERNEL_INTREE_DTS_NAME` in
   `configs/reglinux-s922x.board`.
3. Extend `linux-defconfig.config` or `linux_patches/` if you need extra
  drivers (panel, regulator, battery, etc.).
4. If the board needs a custom boot chain, keep its U-Boot patches in
   `patches/` so the helper scripts pick them up automatically.

Documenting each addition here keeps the fast-growing A311D/S922X matrix
maintainable. 
