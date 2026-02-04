# Qualcomm SM8250 board support

This directory holds the Qualcomm SM8250 (Retroid Pocket family) board support for REGLinux: the dracut configuration, firmware list, kernel patches, and image recipe fragments that are shared across the RP5, Flip2, and Mini variants.

## Layout

- `dracut.conf` – a lean dracut configuration that disables systemd support, limits modules to what REGLinux needs, and explicitly installs the Qual‑comm/ath11k/RTL firmware blobs listed in `kernel-firmware.txt`.
- `fsoverlay/` – overlay content deployed into the running system. `init.d/S06qcom-fan` and `S50btaddr` handle the Qualcomm fan daemon and deterministic Bluetooth MAC generation, while `udev/rules.d/99-retroid-pocket.rules` exposes the Retroid gamepad and haptic device to userspace.
- `kernel-firmware.txt` – the firmware blobs that must be packaged (Adreno 650, SM8250 subsystems, VPU, ath11k Wi-Fi, QCA Bluetooth, and RTL USB Ethernet) so they’re available to the kernel and dracut.
- `linux_sm8250-defconfig.config` – the base kernel configuration extracted from the SM8250 build; keep it in sync with any kernel trees you patch via `linux_patches/`.
- `linux_patches/` – flat list of kernel patches (0000–9999 and named patches) that tune the SM8250 kernel for Retroid hardware: board-specific DTS entries, power-management fixes, audio tweaks, GPU/firmware adjustments, etc. When a board patch is updated, reapply the series to ensure it lines up with your kernel source version.
- `patches/` – package-level patches used by REGLinux: `alsa-lib` enables extended name hints, `alsa-ucm-conf` adds the Retroid UCM profile and legacy loader compatibility, `groovymame` removes the Xrandr dependency, `pipewire` increases the PulseAudio buffer size, and `vita3k` keeps `xxHash` from using the dispatch shim.

## Board-specific pieces (`retroid-sm8250/`)

1. `create-boot-script.sh` – invoked by the build toolchain with `HOST_DIR BOARD_DIR BUILD_DIR BINARIES_DIR TARGET_DIR REGLINUX_BINARIES_DIR`. It copies the kernel `Image`, `rootfs.cpio.lz4`, `reglinux.update`, module/firmware/rescue updates, and the board-specific DTB into `boot/boot/`, then overwrites `efi-part/EFI/BOOT/grub.cfg` with the local version and stages the EFI payload into the final image area.
2. `genimage.cfg` – describes the disk image (`reglinux.img`) layout: a 2 GiB FAT32 `boot.vfat` (label `REGLINUX`) with no extra files other than `@files`, plus a 512 MiB `userdata.ext4` volume (label `SHARE`). `reglinux.img` simply concatenates these partitions.
3. `grub.cfg` – sets a zero-timeout boot menu that launches REGLinux with `fbcon=rotate:3`, `console=ttyMSM0`, `clk_ignore_unused` and `pd_ignore_unused`. RP5 and Flip2 also set `vt.global_cursor_default=0`, while RPmini omits it; each entry points to its own DTB (`sm8250-retroidpocket-*.dtb`).

## Building/updating an image

1. Update or rebuild the kernel tree using `linux_sm8250-defconfig.config` plus the patches in `linux_patches/`, being careful about the order and dependencies (e.g., the DTS patches use `sm8250-retroidpocket-*.dtb` names expected by the boot scripts).
2. Build your rootfs, modules, firmware bundles, and `rescue` image, placing them in the conventional `BINARIES_DIR`.
3. Run the appropriate `rp{5,flip2,mini}/create-boot-script.sh` so it copies the artifacts, configures the EFI partition, and stages the DTB. The script assumes `BINARIES_DIR/efi-part` already contains a generated EFI filesystem with GRUB.
4. Run `genimage` with the matching `genimage.cfg` to produce `reglinux.img` formatted exactly like the example layout (boot FAT + userdata ext4). The final `.img` can then be flashed to the device.

## Notes for contributors

- Keep `dracut.conf` and `kernel-firmware.txt` in sync whenever you add/remove firmware, dracut modules, or host packages that rely on them.
- Prefer patching the kernel inside `linux_patches/` rather than editing the DTS/defconfig in-place; the numbering conveys ordering and dependency.
- When adjusting package sources, drop the new diff into the appropriate `patches/<package>/` directory and ensure it’s applied by the build system.
- Update the board’s `grub.cfg`/`create-boot-script.sh` pair if you ever change kernel command-line flags, DTB names, or EFI layout requirements.
