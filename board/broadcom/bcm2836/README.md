# Broadcom BCM2836 (Raspberry Pi 2) board

## Purpose
This folder captures the board-specific assets for the Broadcom BCM2836 target (Raspberry Pi 2) used by REG-Linux. It provides the boot loader configuration, overlays, kernel configuration, and board hooks required to produce a working image for that platform.

## Boot configuration
* `boot/config.txt` mirrors the default Raspberry Pi firmware settings plus overlay and driver parameters requested for REG-Linux (kernel path, initramfs, disable overscan, audio/bluetooth, VC4 KMS, DPI section, etc.).
* `boot/cmdline.txt` keeps the standard Linux command line for REG-Linux with fastboot, noswap, quiet/splash, and `rootwait` to handle SD card detection.
* `create-boot-script.sh` is the board hook invoked by the build system to copy firmware, kernel, device trees, and artifacts from the binaries directory into `boot/boot`. It also injects this folder's `config.txt`/`cmdline.txt` into the boot partition.

## Filesystem overlays
The `fsoverlay` directory holds the files that are overlaid on top of the root file system:
* `etc/modules.conf` forces the load of `snd_seq` and `i2c_dev`.
* `etc/openal/alsoft.conf` tunes OpenAL for the Solarus engine on Raspberry Pi platforms (no mmap, `periods=10`).

## Kernel configuration
`linux-broadcom32-current.config` contains the full kernel configuration produced for this board (Linux 6.12.55 on arm). It is referenced when building the kernel for the BCM2836 target.

## Patches
Any board-specific patches sit in `patches/`. Right now there is `duckstation-legacy/board-disable-message-OpenGL.patch`, which silences the DuckStation legacy renderer OSD messages when OpenGL is unavailable.

## Build notes
1. Run the REG-Linux build system; it automatically calls `create-boot-script.sh` for this board.
2. Ensure the kernel config and any patches are kept in sync with the target kernel sources if they are rebased.

