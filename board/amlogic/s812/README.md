# REG Linux · Amlogic S812 Support Pack

This folder provides everything the `reglinux-s812` target (`make
s812-build`) needs to turn the generic Buildroot output into images for
Meson8/Meson8m2 based TV boxes (S802/S812 era hardware). It includes the
legacy U-Boot scripts, kernel configuration, device-tree coverage, and
filesystem overlay required by Tronsmart, Minix, MXIII, WeTek, and other
S812 derivatives.

---

## Directory Map

Path | Description
---- | -----------
`boot/` | Pre-made `aml_autoscript.zip`, `s805_autoscript.cmd`, and `uEnv.txt` consumed by vendor U-Boot when booting from SD/USB.
`create-boot-script.sh` | Buildroot post-image hook that wraps the kernel into a `uImage`, creates `uInitrd`, generates both U-Boot scripts via `mkimage`, and stages the DTBs plus update bundles under `boot/`.
`genimage.cfg` | Simple two-partition layout: 2 GiB VFAT boot + 256 MiB `SHARE` EXT4 userdata.
`fsoverlay/` | Minimal overlay shared by all S812 targets (ALSA defaults, CPU/GPU temp helpers).
`linux-defconfig.config` | Complete kernel configuration for the 6.17.x upstream kernel we track.
`linux-defconfig-fragment.config` | Extra bits layered on top of the shared REG Linux kernel fragment (Wayland, Lima GPU, etc.).
`linux_patches/` | Large patch queue that re-enables HDMI/CVBS pipelines, NAND, USB, VPU, PMICs, and remote-control pieces still missing upstream.
`patches/` | Buildroot package fixes: ALSA card aliases for AMlogic AIU/AXG and the PPSSPP GLES2 fallback needed on Lima.

---

## Device Tree Coverage

DTB | Hardware target | Notes
--- | ---------------- | -----
`meson8m2-mxiii.dtb`, `meson8m2-mxiii-plus.dtb` | Tronsmart MXIII / MXIII+ | Dual and quad antenna revisions.
`meson8m2-m8s.dtb`, `meson8m2-m8s-plus.dtb` | M8S / Acemax M8S+ family | `linux_patches/1001-1003` add the vendor-specific quirks.
`meson8m2-wetek-core.dtb` | WeTek Core | Includes Wetek-specific GPIO and NAND wiring.
`meson8-minix-neo-x8.dtb` | Minix Neo X8 | Shares audio/power tree with the MXIII base.
`meson8-tronsmart-s82.dtb` | Tronsmart S82 / M8 | Uses the Cirrus CS4334 codec path patches.

The post-image hook copies every DTB listed above into
`${REGLINUX_BINARIES_DIR}/boot/boot/` so the same SD image can boot a
variety of S812 boxes by editing `uEnv.txt` or renaming DTBs.

---

## Filesystem Overlay

- `etc/asound.conf` and `usr/share/alsa/cards/HDMI.conf` pick sane HDMI
  defaults while leaving the analog codec available as `sysdefault`.
- `usr/bin/cputemp` / `usr/bin/gputemp` mirror the helpers found on Arm
  SBC targets so the frontend can surface SoC temperatures on these TV
  boxes as well.

Drop additional firmware, configs, or helper scripts under
`fsoverlay/`—they’re merged before the initramfs is packed.

---

## Kernel & Patch Stack

`configs/reglinux-s812.board` selects:

- ARMv7 hard-float toolchain + NEON (`BR2_cortex_a9`, `BR2_ARM_EABIHF`)
  and the Lima Mesa driver.
- Linux 6.17.7 with the S812 defconfig (`linux-defconfig.config`), the
  shared REG Linux fragment, and `linux_patches/` to resurrect Meson8/M8m2
  display, NAND, HDMI-CEC, USB OTG, Cirrus audio, and UVC/Sinden gun
  support.
- `BR2_LINUX_KERNEL_UIMAGE=y` with a `0x00208000` load address to match
  the boot ROM expectations and `BR2_TARGET_ROOTFS_CPIO_UIMAGE=y` so the
  initramfs is wrapped as `uInitrd`.
- `BR2_PACKAGE_UBOOT_TOOLS_MKIMAGE=y` to build the `aml_autoscript` and
  `s805_autoscript` binaries needed by vendor U-Boot.

Invoke a build with:

```bash
make s812-build
```

The resulting image lives in
`output/s812/images/reglinux/images/s812/reglinux.img`.

---

## Boot Flow

1. `create-boot-script.sh` copies the freshly built `uImage`,
   `uInitrd`, `reglinux.update`, `modules.update`, `firmware.update`,
   and `rescue.update` bundles into `boot/boot/`.
2. All supported DTBs are staged next to the kernel. Vendors select the
   correct one through the `uEnv.txt` `fdtfile=` entry.
3. The helper runs `mkimage` twice to turn
   `boot/s805_autoscript.cmd` and `boot/aml_autoscript.scr` into the
   binaries expected by legacy AMlogic U-Boot builds, and drops the
   ready-made ZIP for USB booting.
4. `genimage.cfg` packs the FAT/EXT partitions without touching boot
   sectors—vendor U-Boot resides on eMMC/SPI and simply looks for an SD
   card that contains `aml_autoscript`.

---

## Extending S812 Support

1. Add the new DTB name to
   `BR2_LINUX_KERNEL_INTREE_DTS_NAME` (configs/reglinux-s812.board) and
   copy it in `create-boot-script.sh`.
2. If the board needs additional boot parameters, patch
   `boot/uEnv.txt` or ship a board-specific version that users can drop
   onto the FAT partition.
3. Keep kernel/device-specific fixes inside `linux_patches/` and package
   quirks under `patches/` so future upgrades remain reproducible.

Documenting each addition here will keep the aging Meson8/S812 support
approachable for the next refactor. 
