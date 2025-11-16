# REG-Linux Broadcom BCM2835 Board

This directory describes the Raspberry Pi 1 / Zero board target for REG-Linux. It provides the boot artifacts, configuration, overlays, image layout, kernel config, and helper scripts that are specific to Broadcom BCM2835 devices.

## Layout
- `boot/` – contains `config.txt` and `cmdline.txt` that are copied into the boot VFAT partition. These files control the firmware boot path, HDMI tweaks, overlays, audio/drm modules, and the kernel command line flags that the Pi uses when REG-Linux boots.
- `create-boot-script.sh` – the board-specific helper invoked by the build system; it stages firmware, DTBs, kernel, initrd, modules, firmware blobs, and REG-Linux update artifacts under `boot/boot`.
- `fsoverlay/` – filesystem overlay content merged into `/etc` on the target. It currently provides `modules.conf` that preloads `snd_seq`/`i2c_dev` and a tuned `openal/alsoft.conf` optimized for the Pi’s ALSA driver.
- `genimage.cfg` – describes how `boot.vfat`, `userdata.ext4`, and the final `reglinux.img` are laid out so GENIMAGE can produce the flashable image.
- `linux-broadcom32-current.config` – the kernel configuration used for the BCM2835 build (Linux 6.12.55 with Buildroot toolchain metadata).
- `patches/` – drop-in patch sets. The only entry is `patches/thextech/001-no-glesv1_cm.patch.disabled`, which documents a disabled patch for GLESv1_CM; rename/remove it to apply the change.

## Boot configuration
- `boot/config.txt` sets the kernel path (`boot/linux`), points initramfs to `boot/initrd.lz4`, adjusts overscan, enables audio/krnbt/drm, disables firmware KMS probing, and keeps HDMI compatibility tweaks needed for REG-Linux consoles. The PHY boot delay and splash suppression are also curated here.
- `boot/cmdline.txt` feeds the kernel arguments `elevator=deadline`, `vt.global_cursor_default=0`, `logo.nologo`, `label=REGLINUX`, `fastboot`, `noswap`, `quiet`, and `splash` so that the system boots with REG-Linux branding and minimal console noise.

## Filesystem overlay
- `fsoverlay/etc/modules.conf` autoloads `snd_seq` and `i2c_dev` so audio and I²C access are ready before userspace starts.
- `fsoverlay/etc/openal/alsoft.conf` tunes the OpenAL backend for the Pi by disabling `mmap` and increasing `periods` to avoid sound starvation on these CPUs.

## Image generation
- `genimage.cfg` builds a 2 GiB `boot.vfat` partition labeled `REGLINUX` and a 256 MiB `userdata.ext4` partition labeled `SHARE`. It then bundles them into `reglinux.img`, placing the VFAT partition at `1M` and the userdata partition immediately after.

## Kernel configuration & patches
- `linux-broadcom32-current.config` is the exported `make menuconfig` state for the BCM2835 kernel (Linux/arm 6.12.55) with Buildroot’s toolchain metadata, local version suffix `-reglinux`, and the usual Broadcom options preserved.
- `patches/thextech/001-no-glesv1_cm.patch.disabled` is kept for reference but not applied. Rename it without `.disabled` when you want to drop GL ES v1 support.

## Bringing it together
Use the board helper script (`create-boot-script.sh`) after building REG-Linux to copy kernel, initramfs, modules, firmware sets, and overlays into `boot/boot/`, then run GENIMAGE with `genimage.cfg` so the target image matches the Pi’s storage layout. Keep this README up to date if you add firmware files, overlays, or change boot parameters.
