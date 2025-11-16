# Qualcomm SM8550 Board Support

This folder contains the REG-Linux board support artifacts for Qualcomm SM8550-based handhelds such as the AYN Odin2, Odin2 Portal and (eventually) the AYANEO Pocket line. All outputs expect a LinuxLoader-based boot chain and require flashing a custom bootloader that hands control to the `boot/LinuxLoader.cfg` shipped for each board. The AYANEO Pocket S target currently lacks an Android bootloader (ABL), so it cannot boot even though the image staging steps are set up here.

## Layout

### Kernel configuration & firmware
- `linux_sm8550-defconfig.config` is the 6.12.1-based defconfig used as the starting point for the SM8550 kernel build.
- `linux_patches` holds the kernel patch series that enable vendors-specific peripherals (GPU/panel drivers, MMC tweaks, USB/PHY helpers, regulator tweaks, RTC/LED drivers, device tree additions for Odin2/Odin2 Portal/Pocket variants, caches and QoS fixes, etc.). Apply them in order when building the kernel.
- `dracut.conf` describes the minimal initramfs: disable systemd, strip unnecessary modules, include the `busybox-rootfs` dracut module and explicitly install the Qualcomm firmware blobs (`ath12k`, `qcom`, `venus`, etc.) needed by the SoC images.
- `fsoverlay` contains the file-system overlay that ships with the initramfs (fan-daemon startup script, Bluetooth MAC derivation, udev rules for the bundled gamepads and other device-node tweaks plus the supported firmware tree).

### Board-specific artifacts
Each board directory (`odin2`, `odin2portal`, `pockets`) exposes:
1. A `create-boot-script.sh` that copies the kernel image, initramfs, modules, firmware bundle, rescue image and the board’s DTB into `REGLINUX_BINARIES_DIR/boot/boot` so that the final `reglinux.img` contains everything LinuxLoader expects.
2. `genimage.cfg`, which defines a 2 GB FAT boot partition named `REGLINUX` and a 512 MB `userdata` ext4 partition, then wraps them in an HD image that the bootloader can flash.
3. `LinuxLoader.cfg`, the bootloader configuration that points LinuxLoader at the staged kernel/initrd/DTB and tweaks options such as `DisableDisplayHW`, `Target=Linux`, USB host mode and volume-up behavior.

### Device targets
- **AYN Odin2** (and similar SM8550 units): `create-boot-script.sh` copies `qcs8550-ayn-odin2.dtb`, and the bootloader uses the stock `cmdline="clk_ignore_unused pd_ignore_unused quiet rw rootwait label=REGLINUX"`.
- **AYN Odin2 Portal**: mirrors the Odin2 flow but deploys `qcs8550-ayn-odin2portal.dtb` and adds `fbcon=rotate:3` to counter the display orientation quirks; `LinuxLoader.cfg` also keeps `Debug=true` to make troubleshooting easier.
- **AYANEO Pocket S**: staged via the `pockets` directory, which expects `sm8550-ayaneo-ps.dtb` and shares the same kernel `cmdline`. The scripts/bootloader are ready, but the target device lacks a usable ABL, so this build cannot boot yet.

### Package-level tweaks
- `patches/alsa-lib` and `patches/alsa-ucm-conf` add ALSA name hints and UCM configs for the handheld’s audio path (including Retroid Pocket and Pocket S variants).
- `patches/pipewire` increases the PulseAudio compatibility buffer size, `patches/groovymame` disables Xrandr dependency for GroovyMAME, and `patches/vita3k` relaxes xxhash dispatch requirements.

## Build & staging notes
1. Start from `linux_sm8550-defconfig.config`, apply the patches under `linux_patches`, and build the SM8550 kernel and DTBs, making sure to produce all of the `*.dtb` files that each board script expects.
2. Build the rootfs/rescue images using the usual REGLinux tooling; dracut will read `dracut.conf` and bundle `fsoverlay`.
3. Invoke the board-specific `create-boot-script.sh` from the REGLinux packaging workflow so that `boot/boot/` receives `linux`, `initrd.lz4`, `modules.update`, `firmware.update`, `rescue.update` and the desired DTB.
4. Run `genimage` with the supplied `genimage.cfg` to produce `reglinux.img`. The resulting image contains the FAT boot partition plus the `userdata` share expected by LinuxLoader.
5. Flash the custom LinuxLoader (e.g., via the vendor toolchain or the bootloader installer you already use) so the board boots the freshly generated image. Each `LinuxLoader.cfg` already sets `Target=Linux`, enforces `DisableDisplayHW=true` where needed, and disables USB host mode unless explicitly required.

## Notes
- These images are LinuxLoader-only; there is no stock firmware fallback. A custom loader is required before the board can boot into REGLinux.
- The overlay scripts in `fsoverlay/etc/init.d` handle fan control and Bluetooth MAC generation, while `fsoverlay/etc/udev/rules.d`/`usr/lib/udev/rules.d` ensure the handhelds’ gamepads behave as joysticks and not mice.
- Keep `Install` firmware entries in `dracut.conf` synchronized with the `/usr/lib/firmware` content you ship; the list already enumerates Qualcomm-specific blobs such as `ath12k` and `venus-*`.

## Status
- **AYN Odin2 / Odin2 Portal** – supported with custom bootloader and DTBs.
- **AYANEO Pocket S** – staging scripts exist but the board is currently unbootable because there is no available Android bootloader (ABL) to chain from; upstream LinuxLoader needs a usable payload before REGLinux can run.
