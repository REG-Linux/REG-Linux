# REG-Linux Broadcom boards

This directory collects the board-specific assets that REG-Linux packages for each Broadcom SoC. Every subdirectory holds the firmware configs (`boot/config.txt`, `boot/cmdline.txt`), `fsoverlay/`, `genimage.cfg`, kernel configs, helper scripts (`create-boot-script.sh`), and any patches needed to build an image for that family. Build automation feeds the standard directory variables (`HOST_DIR`, `BOARD_DIR`, `TARGET_DIR`, etc.) and relies on the board README to document layout and workflow.

## Boards in this tree

### `bcm2711` – Raspberry Pi 4 / Compute Module 4 / Pi 400
- Targets the 64-bit BCM2711 SoC; packaging stages `Image`, modules, firmware, initramfs, squashfs/rescue images, device trees and supporting payloads before running `genimage`.
- `boot/config.txt`/`cmdline.txt` prefer 64-bit mode, DRM/KMS, HDMI tweaks, `elevator=deadline`, `rootwait`, and `noswap` to keep the console quiet.
- `fsoverlay/` currently forces `snd_seq` and `i2c_dev` plus any extra files you need merged into the root filesystem.
- Patches for `groovymame`, `libretro-yabasanshiro`, and `sugarbox` live under `patches/` and are applied in build order; use the numbered filenames to control ordering.
- Reference `linux-broadcom64-current.config` when reproducing or auditing the kernel for this board. (`bcm2711/README.md`)

### `bcm2712` – Raspberry Pi 5 / Pi 500
- Describes the boot layout (2 GiB FAT `REGLINUX`, 512 MiB ext4 `userdata`, final `reglinux.img`) and the helper scripts that copy the firmware tree, blobs, DTBs, and kernel artifacts into `REGLINUX_BINARIES_DIR`.
- Boot config enables 64-bit kernel, DRM/KMS, default HDMI/audio/BT tweaks, `rootwait`/`fastboot`/`noswap`, and ships the `pironman5` overlay for Pi 5 hardware.
- `fsoverlay/etc/modules.conf` loads `snd_seq` and `i2c_dev`, while `patches/` holds board fixes for `groovymame`, `libretro-yabasanshiro`, and `sugarbox` to keep DRM-only graphics and GLES builds stable.
- Kernel configuration is captured in `linux-broadcom64-current.config`. (`bcm2712/README.md`)

### `bcm2837` – Raspberry Pi 3 / Zero 2
- 64-bit config that requests `arm_64bit=1`, loads `boot/linux` & `bootstrap`, and tunes DRM, audio, HDMI, and quiet boot flags; `cmdline` adds `fastboot`, `noswap`, and quiet branding.
- `create-boot-script.sh` stages firmware, DTBs, kernels, modules, and update artifacts before `genimage` lays out a 2 GiB FAT `REGLINUX` and 256 MiB ext4 `SHARE` partition.
- Overlay forces `snd_seq`/`i2c_dev` and adjusts OpenAL (`periods`, disable `mmap`); patches quiet DuckStation’s OpenGL notices and drop SwitchRes Xrandr dependencies.
- Keep `linux-broadcom64-current.config` in sync with Kerunel sources, and update overlay/patch docs if you change boot or firmware expectations. (`bcm2837/README.md`)

### `bcm2836` – Raspberry Pi 2
- Boot scripts copy firmware/kernel/DTBs into the boot partition, and `boot/config.txt`/`cmdline.txt` mirror the Raspberry Pi defaults plus REG-Linux-specific overlays (VC4, DPI, audio).
- Overlay `etc/modules.conf` and OpenAL tuning matches the Solarus engine, while `patches/duckstation-legacy` silences legacy renderer messages when OpenGL isn’t available.
- The kernel config `linux-broadcom32-current.config` documents the Linux 6.12.55/arm option set used for BCM2836 roots. (`bcm2836/README.md`)

### `bcm2835` – Raspberry Pi 1 / Zero
- Boot layout and `genimage.cfg` produce a 2 GiB FAT `REGLINUX` volume and 256 MiB `userdata.ext4` partition, with `create-boot-script.sh` copying firmware, modules, and overlay files into `boot/boot`.
- Config files adjust overscan, enable audio/DRM, tune HDMI/PHY delays, and supply `elevator=deadline`, `quiet`, and REG-Linux branding via `cmdline.txt`.
- Overlay ensures `snd_seq`/`i2c_dev` preload and tunes OpenAL to avoid mmap issues; the kernel config is saved in `linux-broadcom32-current.config`.
- Includes a disabled patch reference for `thextech` GLESv1, which can be applied by renaming/removing `.disabled`. (`bcm2835/README.md`)

## Common workflow reminders
- Run REG-Linux’s build system; it sets the required environment vars, runs `create-boot-script.sh`, and invokes `genimage` with the board’s configuration.
- Edit the overlay, config, or patch folders before building so your changes are copied into `REGLINUX_BINARIES_DIR` and captured on the final image.
- When adjusting firmware, kernel, or patch logic, keep the matching README section up to date to help future maintainers understand what each file affects.
