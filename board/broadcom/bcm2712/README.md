# Broadcom BCM2712 Board

This board directory defines the Raspberry Pi 5 / Raspberry Pi 500 support for REG-Linux. It collects the boot configuration, filesystem overlays, patches, and helper scripts that the build system packages into the final `reglinux.img` image for Broadcom BCM2712 hardware.

## Image layout
- `genimage.cfg` drives the OEM image creation. The boot partition is a 2 GiB FAT32 volume labeled `REGLINUX`, while userdata is a 512 MiB ext4 share under `/userdata`. `reglinux.img` is layered on top of those files so it can be flashed as a single HD-style image.

## Boot configuration
- `boot/config.txt` enables the 64-bit kernel, DRM/KMS drivers, default audio/BT/clock settings, and includes Raspberry Pi specific tweaks such as HDMI delay, overscan handling, and `vc4-kms-v3d` with extra CMA headroom.
- `boot/cmdline.txt` keeps `rootwait`, `fastboot`, and `noswap` active so the kernel finds the rootfs quickly and the console stays quiet during boot.

## Packaging helper
- `create-boot-script.sh` is invoked by the board build pipeline to copy the pre-built `Image`, firmware tree, Device Tree blobs, modules bundle, and `initrd`/squashfs artifacts into `REGLINUX_BINARIES_DIR`. It also pulls in the board `boot` configs and the `pironman5` overlay (`sunfounder-pironman5.dtbo`) required on Pi 5-ish hardware.

## Filesystem overlay
- `fsoverlay/etc/modules.conf` lists `snd_seq` and `i2c_dev`, ensuring the kernel loads the sequencer and I²C helpers early on target systems.

## Board-specific patches
These patches are stored under `patches/` and applied to the userland tree during the build:
1. `groovymame/switchres-no-xrandr.patch` removes the Xrandr dependency from switchres, forcing the renderer to use DRM/KMS only and cleaning up verbose logging format specifiers.
2. `libretro-yabasanshiro/001-workaround-mesa-shaders.patch` makes texture coordinate arithmetic more precise (adding `round` calls) to work around Mesa shader issues on Mali/VC-based GPUs.
3. `sugarbox/001-gles.patch` preserves multisampling and injects a `mediump` precision qualifier so Sugarbox can compile its GLSL shaders with the GLES driver stack on BCM2712.

## Kernel configuration
- `linux-broadcom64-current.config` is the kernel config snapshot used for the BCM2712 kernel build; it ensures all Broadcom-specific drivers and kernel features required by REG-Linux are enabled.

## Notes
- Review `boot/config.txt` comments before tweaking HDMI or overlay settings so the Raspberry Pi 5 hardware boots reliably.
- Keep the patches in sync with upstream revisions; they are applied non-interactively during the REG-Linux build.
