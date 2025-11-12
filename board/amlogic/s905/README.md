# REG Linux · Amlogic S905/S905X/S905D Support Pack

`board/amlogic/s905/` hosts the assets consumed by the
`reglinux-s905` Buildroot target (`make s905-build`). It covers a broad
set of Meson GXBB/GXL boards—Khadas VIM1, Libretech Le Potato (v1/v2),
Odroid-C2, NanoPi K2, P200/P201 TV boxes, FunKey R1, and a “generic”
S905 TV box image. Each subdirectory contains the boot scripts, image
layout, and optional U-Boot build recipe for that board, while the
top-level overlay/patches keep audio, temps, and Wayland packages
consistent across the fleet.

---

## Directory Map

Path | Description
---- | -----------
`fsoverlay/` | Shared ALSA policy and temperature helper scripts for every GXBB/GXL build.
`fun-r1/`, `khadas-vim1/`, `lepotato*/`, `minix-neo-u1/`, `nanopi-k2/`, `odroid-c2/`, `p201/`, `s905-tvbox/` | Per-board boot assets (`boot/`), `create-boot-script.sh`, `genimage.cfg`, and optional `build-uboot.sh`.
`patches/uboot/` | Patch set applied to every mainline U-Boot build (suppress HDMI console, keep stdout on UART, prefer USB/NVMe boot, etc.).
`patches/ppsspp` & `patches/mupen64plus*` | Emulator fixes so Lima+Wayland renders correctly on these 32/64-bit Mali GPUs.

Each board directory follows the same structure: optional
`build-uboot.sh`, the post-image hook, a `boot/` payload (extlinux,
uEnv/aml_autoscript, logos), and a `genimage.cfg`.

---

## Board Highlights

Board dir | Device tree(s) | Notes
--------- | --------------- | -----
`fun-r1/` | `meson-gxl-s905x-fun-r1.dtb` | Wraps the kernel as a legacy `uImage`/`uInitrd` pair and generates both AML and S905 autoscripts; designed for the FunKey R1 handheld.
`khadas-vim1/` | `meson-gxl-s905x-khadas-vim.dtb` | Builds mainline U-Boot (2025.01) plus LibreELEC FIP, then chain-loads it via the vendor scripts on eMMC/SPI. Drops every Khadas script (`boot.ini`, `aml_autoscript`, etc.) onto the FAT partition and copies `u-boot.bin` as `u-boot.bin` for the vendor boot ROM to find.
`lepotato/` | `meson-gxl-s905x-libretech-cc.dtb` | Mainline U-Boot build (libretech-cc_defconfig) with FIP packaging; boots via extlinux.
`lepotato-v2/` | `meson-gxl-s905x-libretech-cc-v2.dtb` | Re-uses the same U-Boot sources as `lepotato/` but switches to the v2 defconfig and DTB.
`minix-neo-u1/` | `meson-gxbb-minix-neo-u1.dtb` | Uses the `p200` mainline defconfig for U-Boot, stages an extlinux entry, and keeps HDMI console disabled.
`nanopi-k2/` | `meson-gxbb-nanopi-k2.dtb` | Mainline `nanopi-k2_defconfig` + LibreELEC FIP; standard extlinux layout.
`odroid-c2/` | `meson-gxbb-odroidc2.dtb` | Builds 2025.01 U-Boot (`odroid-c2_defconfig`), applies the shared patches, and publishes an extlinux boot.
`p201/` | `meson-gxbb-nexbox-a95x.dtb` | Targets the P201/Nexbox A95X design (S905). Layout mirrors Minix/NanoPi boards.
`s905-tvbox/` | `meson-gxbb-minix-neo-u1.dtb`, `meson-gxbb-nexbox-a95x.dtb`, `meson-gxl-s905d-p230.dtb`, `meson-gxl-s905d-p231.dtb`, `meson-gxl-s905w-p281.dtb`, `meson-gxl-s905w-tx3-mini.dtb`, `meson-gxl-s905x-p212.dtb` | Generic TV-box image: copies a bundle of GXBB/GXL DTBs, keeps the kernel as `uImage`, and generates AML+S905 autoscripts so it boots on most P200/P201/P212/S905W devices without reflashing U-Boot.

---

## Shared Overlay & Patches

- `fsoverlay/etc/asound.conf` points ALSA `default` at HDMI, keeping the
  analog codec unmuted as `sysdefault`.
- `fsoverlay/usr/bin/cputemp` and `gputemp` expose SoC thermals to the
  frontend UI.
- `patches/uboot/*.patch` is applied by every `build-uboot.sh` helper
  (Le Potato, NanoPi K2, Odroid-C2, Khadas VIM1, Minix, P201). They
  silence the framebuffer console, prevent the boot log from hijacking
  HDMI, and adjust device names so `fdtdir /boot/boot` works.
- Emulator/SDL patches keep Wayland+KMS stable with the Lima driver.

Boards such as Fun-R1 and `s905-tvbox` still rely on vendor U-Boot, so
their post-image scripts generate AML autoscripts instead of extlinux
entries. The rest use mainline U-Boot + extlinux.

---

## Build Integration

Key points from `configs/reglinux-s905.board`:

- Targets Cortex-A53 (`BR2_cortex_a53`, `-march=armv8-a+crypto+crc`) and
  enables the Lima EGL stack, SWAY compositor, and Zstd-compressed
  SquashFS root.
- Pulls the upstream kernel defconfig from
  `board/amlogic/linux-meson64-current.config` plus the shared REG Linux
  fragment, and builds the DTBs listed in `BR2_LINUX_KERNEL_INTREE_DTS_NAME`
  (Nanopi K2, Odroid-C2, Khadas VIM1, Libretech CC v1/v2, p20x boards,
  etc.).
- Applies both the shared `board/amlogic/linux_patches` queue and the
  `board/reglinux/linux_patches/aarch64` fixes.
- Adds overlays in this order:
  `board/fsoverlay`, `board/amlogic/fsoverlay`, and
  `board/amlogic/s905/fsoverlay`.
- Keeps the initramfs in LZ4 format (`rootfs.cpio.lz4`), but Fun-R1 and
  the TV box image rewrap it as `uInitrd`.

Build it with:

```bash
make s905-build
```

Artifacts appear under
`output/s905/images/reglinux/images/<board>/`.

---

## Boot & Image Layout

- Extlinux-based boards (`khadas-vim1`, `lepotato*`, `nanopi-k2`,
  `odroid-c2`, `minix-neo-u1`, `p201`) stage `Image`, `initrd.lz4`,
  `reglinux.update`, and their DTB into `boot/boot/`, then copy the
  matching `boot/extlinux.conf`.
- Boards that must chain-load vendor U-Boot drop additional payloads:
  - Khadas VIM1 copies `boot.ini`, `boot.scr`, `aml_autoscript*`, and
    writes `u-boot.bin` from the freshly built mainline image so the
    vendor ROM can load it off the SD card root.
  - Fun-R1 and the generic TV box convert the kernel to `uImage`,
    produce AML/S905 autoscripts via `mkimage`, and include
    `boot/uEnv.txt` so a user can pick the correct DTB without editing
    `extlinux.conf`.
- Most `genimage.cfg` files create a 2 GiB FAT32 boot partition followed
  by a 256 MiB EXT4 userdata slice. Khadas/Odroid images add U-Boot blobs
  where necessary.

---

## Extending S905 Support

1. Copy the closest board directory and update:
   - DTB staging logic inside `create-boot-script.sh`.
   - Serial console / kernel args in `boot/extlinux.conf` or `uEnv.txt`.
   - FIP target inside `build-uboot.sh` (if you need a new mainline
     U-Boot build).
2. Add the DTB to `BR2_LINUX_KERNEL_INTREE_DTS_NAME` in
   `configs/reglinux-s905.board`.
3. Drop per-board firmware or helpers inside `fsoverlay/` if needed, or
   extend `patches/` when Buildroot packages require adjustments.

Document the change in this README so the growing list of GXBB/GXL
targets remains understandable. 
