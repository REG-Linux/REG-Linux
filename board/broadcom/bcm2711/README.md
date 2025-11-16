# BCM2711 (Raspberry Pi 4/CM4/400) board support

This directory contains the board-specific bits that REG-Linux needs when targeting Broadcom BCM2711-based hardware. The higher-level build infrastructure supplies the `HOST_DIR`, `BOARD_DIR`, `BUILD_DIR`, `BINARIES_DIR`, `TARGET_DIR` and `REGLINUX_BINARIES_DIR` variables and runs `create-boot-script.sh` (see below) to gather firmware, kernel, initramfs and supplementary payloads.

## Layout

- `boot/` – `config.txt` and `cmdline.txt` define the Raspberry Pi firmware settings and kernel command line. Any changes made here ship directly to the VFAT boot partition.
- `create-boot-script.sh` – invoked by the REG-Linux packaging flow; copies `rpi-firmware`, `.dtb` files, kernel artifacts and update images into `REGLINUX_BINARIES_DIR/boot/*` so that they are included in the final boot image.
- `genimage.cfg` – describes how `genimage` composes the `boot.vfat`, `userdata.ext4` and final `reglinux.img` when building release media for BCM2711 boards.
- `linux-broadcom64-current.config` – the full kernel configuration used for the 64-bit Broadcom kernel shipped with this board. Reference this file if you need to reconfigure, audit options or reproduce the kernel build.
- `fsoverlay/` – overlay root contents that are merged into the target filesystem. Currently specifies additional kernel modules to load at boot (`/etc/modules.conf` enables `snd_seq` and `i2c_dev`).
- `patches/` – per-package patches applied during the REG-Linux build. Each subdirectory corresponds to a package name (`groovymame`, `libretro-yabasanshiro`, `sugarbox`) and contains the patch files that are applied in order.

## Boot configuration highlights

- `boot/config.txt` enables 64-bit mode, points the firmware to `boot/linux` and `boot/initrd.lz4`, tweaks HDMI defaults (auto-display detect, disable overscan, disable splash, enable audio/Bluetooth/VC4/KMS), raises `boot_delay` to smooth HDMI sync and turns on `arm_boost` so the board runs near full speed.
- `boot/cmdline.txt` sets `elevator=deadline` I/O scheduling, hides the boot logo, and requests a quiet boot with `rootwait`, `fastboot` and `noswap` to align with REG-Linux’s embedded use-case.

## Packaging and deployment

1. Build outputs under `BINARIES_DIR` must include at least `Image`, `modules`, `firmware`, `rootfs.cpio.lz4`, `rootfs.squashfs`, `rescue`, the `rpi-firmware` tree and any required `.dtb` files.
2. `create-boot-script.sh` copies those artifacts plus `boot/config.txt` and `boot/cmdline.txt` into `REGLINUX_BINARIES_DIR/boot`, placing the kernel/initramfs under `boot/boot/` so the Raspberry Pi firmware can load them.
3. `genimage.cfg` was tuned for compatibility with `genimage`/mtools on Linux hosts and lays out the boot and userdata partitions before creating `reglinux.img`. Review the inline comments if you need to adjust partition sizes.

## Working with kernel patches

- Drop new patches into the appropriate `patches/<package>` directory and ensure their filenames respect the load ordering (prefixed with numbering is recommended).
- These patches are typically consumed by the REG-Linux build scripts, so double-check the package’s `Config.in` file or the buildroot package definition if you add new entries.

## Overlay additions

Place any extra files you need under `fsoverlay/` (matching the target root layout). They will be merged into the final root filesystem during image creation. Currently, only `/etc/modules.conf` exists to force-load `snd_seq` and `i2c_dev`.

## Notes

- This board configuration supports Raspberry Pi 4, Compute Module 4 and Pi 400 models running the 64-bit Broadcom `bcm2711` SoC.
- For a full reproduction of the kernel, feed `linux-broadcom64-current.config` into `make olddefconfig` from the kernel source tree before building.
- If you need to override firmware behavior, edit `boot/config.txt`/`cmdline.txt` and re-run the create-boot-script step so that the updated payloads land in the final image.
