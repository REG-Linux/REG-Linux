# REG Linux · Amlogic S905 Gen2 (GXM/G12A) Support Pack

The `reglinux-s905gen2` target (`make s905gen2-build`) consumes
everything in this directory to build images for Khadas VIM2 (S912/GXM)
and Radxa Zero (G12A/S905Y2). It supplies the board-specific boot logic,
U-Boot helpers, Wi‑Fi firmware overlay, and extra Buildroot patches
needed by these mid-generation Meson boards.

---

## Directory Map

Path | Description
---- | -----------
`khadas-vim2/` | Boot assets + U-Boot build recipe for the VIM2 (GXM).
`radxa-zero/` | Same structure for Radxa Zero (G12A/S905Y2), including board-specific U-Boot patches.
`fsoverlay/` | Adds the Broadcom 43456 firmware + NVram needed by the Radxa Zero and keeps HDMI ALSA defaults aligned with other AMlogic targets.
`linux-defconfig-fragment.config` | Extra kernel options layered on top of `board/amlogic/linux-meson64-current.config` (Panfrost, Wayland, etc.).
`patches/` | Package tweaks shared by these boards: mainline U-Boot adjustments, EmulationStation TTY fix, and the Glide64 GLES2 workaround.

Each board directory ships `create-boot-script.sh`, `boot/extlinux.conf`,
`genimage.cfg`, and `build-uboot.sh`.

---

## Board Highlights

Board dir | Device tree(s) | Notes
--------- | --------------- | -----
`khadas-vim2/` | `meson-gxm-khadas-vim2.dtb` | Downloads U-Boot 2025.01, applies the shared `patches/uboot/*.patch`, builds `khadas-vim2_defconfig`, packages it via LibreELEC’s `amlogic-boot-fip`, and stages `Image`, `initrd.lz4`, the SquashFS update set, and DTB under `boot/boot/`. Booted through extlinux.
`radxa-zero/` | `meson-g12a-radxa-zero.dtb` | Same flow but with Radxa’s board-specific patches in `radxa-zero/patches/uboot`. `create-boot-script.sh` copies Radxa’s extlinux entry and the board’s DTB; `build-uboot.sh` emits `uboot-radxa-zero/` so `genimage` can inject it when needed.

---

## Overlay & Package Patches

- `fsoverlay/lib/firmware/brcm/*` ships the FW/NVRAM pair for the AP6256
  Wi‑Fi module so the initramfs can talk to the SDIO chip before the
  root filesystem is expanded.
- `patches/uboot/*.patch` tweak the global Meson64 defconfigs so U-Boot
  looks for DTBs under `/boot/boot/`, keeps stdout on UART, and drops
  the `amlogic/` prefix that breaks `fdtdir`.
- `patches/batocera-emulationstation/001-fixtty.patch` points
  EmulationStation at the current VT so it can respawn cleanly on the
  framebuffer/Wayland bridge.

Drop additional firmware blobs into `fsoverlay/` if another Gen2 board
requires them.

---

## Build Integration

Highlights from `configs/reglinux-s905gen2.board`:

- Targets Cortex-A53 with Crypto extensions,
  `BR2_PACKAGE_SYSTEM_PANFROST_MESA3D=y`, and enables SWAY/Wayland by
  default.
- Applies the shared AMlogic kernel patches plus the REG Linux
  aarch64 fixes; additional options enter through
  `linux-defconfig-fragment.config`.
- Enables `BR2_PACKAGE_HOST_AML_DTBTOOLS`, `BR2_PACKAGE_HOST_PYTHON_MKBOOTIMG`,
  and `BR2_PACKAGE_HOST_MESON_TOOLS` so the post-image scripts can
  repack AMlogic boot headers when needed.
- Adds `BR2_PACKAGE_RZERO_UBOOT` so Radxa’s vendor boot blob is available
  even if you do not run `build-uboot.sh`.
- Uses LZ4-compressed initramfs + Zstd-compressed SquashFS (`reglinux.update`).

Build command:

```bash
make s905gen2-build
```

Images end up under
`output/s905gen2/images/reglinux/images/<board>/`.

---

## Boot & Image Layout

- `create-boot-script.sh` on each board copies `Image`,
  `rootfs.cpio.lz4` (→ `initrd.lz4`), `reglinux.update`, `modules.update`,
  `firmware.update`, `rescue.update`, and the DTB into `boot/boot/`, and
  drops the matching `boot/extlinux.conf`.
- The helper stage a board-specific `build-uboot-*/` folder, runs the
  `build-uboot.sh` script, and leaves the resulting FIP bundle under
  `REGLINUX_BINARIES_DIR/uboot-*` so `genimage` or fastboot installers
  can reuse it.
- `genimage.cfg` (one per board) keeps the usual 2 GiB boot / 256 MiB
  userdata layout, but you can bump sizes per board if required.

---

## Extending S905 Gen2 Support

1. Clone the closest board directory and update the DTB staging and
   serial console settings in `boot/extlinux.conf`.
2. Add the new DTB to `BR2_LINUX_KERNEL_INTREE_DTS_NAME` inside
   `configs/reglinux-s905gen2.board`.
3. Update `linux-defconfig-fragment.config` if the new board needs extra
  drivers (touch panels, regulators, etc.), and drop any required
  firmware into `fsoverlay/`.
4. Keep additional U-Boot/fel patches in `patches/uboot/` so the build
  system automatically applies them when `build-uboot.sh` runs.

Record any quirks here so the Gen2 support matrix remains easy to grasp. 
