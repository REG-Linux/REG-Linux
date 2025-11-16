# Broadcom BCM2837 Board (Raspberry Pi 3 / Zero 2)

This directory contains the board-specific assets that let REG-Linux run on Broadcom BCM2837 platforms (Raspberry Pi 3 and the Raspberry Pi Zero 2). It describes how the boot partition is populated, which overlays and kernel configuration we ship, and what patches we apply when building supported third-party software.

## Directory layout

- `boot/`: `config.txt` and `cmdline.txt` are the Raspberry Pi firmware configuration files applied to the FAT boot partition. They request the 64-bit kernel (`arm_64bit=1`), load `boot/linux`, `boot/initrd.lz4`, and configure DRM, audio, Bluetooth, and HDMI fallbacks suitable for kiosk/console use. `cmdline.txt` passes `rootwait fastboot noswap` along with a quiet splash entry to hide the boot noise.

- `create-boot-script.sh`: Invoked by the REG-Linux build system to stage firmware, DTBs, kernels, initramfs/rootfs, and the boot configs into `REGLINUX_BINARIES_DIR/boot` (`linux`, `modules.update`, `firmware.update`, `initrd.lz4`, etc.). The script expects the usual build arguments (`HOST_DIR`, `BOARD_DIR`, `BUILD_DIR`, `BINARIES_DIR`, `TARGET_DIR`, `REGLINUX_BINARIES_DIR`), so the board just needs to make the proper files available in those paths before the script runs.

- `genimage.cfg`: Defines the partition layout embedded in `reglinux.img`. The boot FAT partition is 2 GB and labelled `REGLINUX`, while user data lives in a 256 MB `SHARE` ext4 partition. `userdata` contents can be dropped under `TARGET_DIR/userdata` before running genimage.

- `linux-broadcom64-current.config`: The kernel configuration we use for BCM2837 builds. Keep it in sync with your kernel sources if you reconfig the kernel or swap to a newer branch.

- `fsoverlay/`: Files that go into the root filesystem overlay.
  - `etc/modules.conf` lists the kernel modules auto-loaded at boot, currently `snd_seq` and `i2c_dev`.
  - `etc/openal/alsoft.conf` tweaks ALSA/mmap settings for Solarus-engine-on-RPi audio, increasing `periods` and disabling `mmap`.

- `patches/`: Directory of board-applied patches.
  - `duckstation-legacy/board-disable-message-OpenGL.patch` removes the OpenGL warning message when the hardware renderer is unavailable so the RPi UI stays quiet and falls back to the software renderer cleanly.
  - `groovymame/switchres-no-xrandr.patch` disables the SwitchRes Xrandr backend and fixes some logging format specifiers, which simplifies builds on systems that only support DRM/KMS.

## Usage notes

1. Build REG-Linux as usual; when the board-specific stage runs it will call `create-boot-script.sh` and copy the contents of `boot/` into the generated image.
2. If you need to customize the firmware/boot experience (e.g., HDMI modes, overlays, or kernel modules), edit the files under this directory before building so the updated configs are staged.
3. Patches under `patches/` are applied by the relevant package recipes—keep them up to date if the upstream sources change.

## Licensing & attribution

The scripts and configs here inherit the same license as REG-Linux. The patches include their original headers, which should be preserved when updating them.
