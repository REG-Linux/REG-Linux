# REG Linux · Allwinner H3 Support Pack

Everything in this directory is pulled in when building the
`reglinux-h3` target (`make h3-build`). It contains the per-board boot
assets, filesystem overlays, and patches that turn the generic Buildroot
output into images for Allwinner H2+/H3 Cortex‑A7 boards.

---

## Directory Map

Path | Description
---- | -----------
`bananapi-m2-zero/` | Boot script, extlinux entry, and `genimage.cfg` for the Banana Pi M2 Zero (`sun8i-h2-plus-bananapi-m2-zero.dtb`).
`cha/` | Capcom Home Arcade support package: boot assets, dedicated overlay, Wi‑Fi firmware list, and image recipe.
`orangepi-one/` | Assets for `sun8i-h3-orangepi-one`.
`orangepi-pc/` | Assets shared by Orange Pi PC and PC Plus – the boot script copies both DTBs.
`orangepi-pc-plus/` | Dedicated layout for the PC Plus variant when a separate image is desirable.
`orangepi-plus2e/` | Assets for Orange Pi Plus 2E board `sun8i-h3-orangepi-plus2e`.
`fsoverlay/` | H3-wide filesystem overlay (ALSA routing, temperature helpers, etc.) merged into every build of this SoC family.
`cha/fsoverlay/` | Overlay that only ships with the Capcom Home Arcade (EmulationStation defaults, system configs).
`patches/` | Package-level tweaks that only apply when building `reglinux-h3` (currently `ppsspp/002-force-gles20-lima.patch` to stay on a Lima-compatible GLES2 renderer).

Each board directory follows the same structure:

* `create-boot-script.sh` – Buildroot post-image hook that stages the
  kernel (`zImage` → `/boot/linux`), initrd, SquashFS (`reglinux.update`),
  `modules.update`, `firmware.update`, `rescue.update`, and the relevant
  DTBs into the REG Linux boot partition.
  The script now also invokes `../build-uboot.sh` to rebuild U-Boot 2025.01
  with the common Allwinner H3 patch/config fragments and stages the
  resulting `u-boot-sunxi-with-spl.bin` under `reglinux/uboot-<board>/`.
* `boot/extlinux.conf` – Syslinux-style boot entry pointing at the staged
  kernel and DTB (e.g., the Capcom Home Arcade renames its DTB to
  `capcom-home-arcade.dtb`).
* `genimage.cfg` – SD/eMMC image layout (partition sizes, labels, file
  systems) used in Buildroot’s `genimage` step.

Use one of the existing folders as a baseline when introducing another
H3-based board.

---

## Board Highlights

Board | Notes
----- | -----
Banana Pi M2 Zero | Copies `sun8i-h2-plus-bananapi-m2-zero.dtb`; otherwise follows the standard layout.
Capcom Home Arcade (`cha/`) | Includes `kernel-firmware.txt` listing RTL8188EU blobs, plus an overlay that seeds EmulationStation settings in `usr/share/reglinux/datainit/system/configs/emulationstation/es_settings.cfg`.
Orange Pi One | Minimal H3 target (`sun8i-h3-orangepi-one.dtb`).
Orange Pi PC / PC Plus | `orangepi-pc/create-boot-script.sh` exports both `.dtb` files so a single image boots PC or PC Plus.
Orange Pi PC Plus (dedicated) | Kept for completeness when per-board tuning is required.
Orange Pi Plus 2E | Ships its own DTB (`sun8i-h3-orangepi-plus2e.dtb`) and image recipe.

---

## Filesystem Overlays

Overlay | Contents / Purpose
------- | -------------------
`fsoverlay/etc/asound.conf` | Routes the internal codec so ALSA defaults to the H3 analog output.
`fsoverlay/usr/bin/cputemp` & `gputemp` | Tiny helpers used by the frontend to read SoC temperatures.
`cha/fsoverlay/.../es_settings.cfg` | Capcom Home Arcade EmulationStation defaults (themes, input mappings, etc.).

Drop persistent configuration, helper scripts, or device‑specific data
into these overlays when adjusting Buildroot packages is unnecessary.

---

## Build Integration

* Buildroot configuration: `configs/reglinux-h3.board`
  * Enables ARMv7 hard-float, NEON/VFPv4, Lima Mesa (`BR2_PACKAGE_SYSTEM_LIMA_MESA3D=y`),
    Wayland/Sway, SPI flash tools, and selects the overlays listed above via
    `BR2_ROOTFS_OVERLAY`.
  * Requests the DTBs for Banana Pi M2 Zero and the supported Orange Pi
    variants (`BR2_LINUX_KERNEL_INTREE_DTS_NAME`).
  * Adds kernel fragments `board/allwinner/linux-sunxi32-current.config`
    plus `board/reglinux/linux-defconfig-reglinux.config`.
  * Points `BR2_GLOBAL_PATCH_DIR` to both the shared Allwinner patch
    directory and `board/allwinner/h3/patches`.
* Build invocation:

  ```bash
  make h3-build
  ```

  Artifacts appear under `output/h3/images/reglinux/images/<board>/`.

---

## Boot Firmware Notes

* `cha/kernel-firmware.txt` lists the Wi‑Fi/Bluetooth firmware blobs that
  must be packaged for the Capcom Home Arcade (RTL8188EU family).
* `build-uboot.sh` can optionally clone TF-A `lts-v2.10.12` and rebuild the
  BL3x payload when `UBOOT_ATF_PLATFORM` is defined, but by default it sticks
  to the legacy H3 flow (no upstream TF-A port exists for these 32-bit SoCs).
* Every board stages its DTB(s) into `/boot/boot/` next to `linux`, the
  initrd, `reglinux.update`, `modules.update`, `firmware.update`, and
  `rescue.update`. The shared `build-uboot.sh` helper caches the U-Boot
  source under `reglinux/build-uboot-cache/`, applies
  `patches/u-boot/*.patch` + the merged config fragment, and publishes
  `uboot-<target>/u-boot-sunxi-with-spl.bin`; `genimage.cfg` picks that
  file up via `../uboot-<target>/...` when emitting the raw disk image.

---

## Extending H3 Support

1. **Copy the closest board directory** and adjust:
   * DTB names staged in `create-boot-script.sh`.
   * The `FDT` entry inside `boot/extlinux.conf`.
   * Partition sizes or labels inside `genimage.cfg` if the storage layout
     differs.
2. **Update `configs/reglinux-h3.board`** with additional DTBs or feature
   selects needed by the new hardware.
3. **Add overlays or patches** in `fsoverlay/`, `cha/fsoverlay/`, or
   `patches/` only when the change cannot be expressed through standard
   Buildroot options.

Maintaining this structure keeps per-board drift low and makes it easy to
follow the full image creation pipeline from raw Buildroot outputs to the
final REG Linux SD card image.
