# Qualcomm SM8550 Board Support

This folder contains the REG-Linux board support artifacts for Qualcomm SM8550-based handhelds such as the AYN Odin2, Odin2 Portal and (eventually) the AYANEO Pocket line. All outputs expect a GRUB-based boot chain and require flashing a custom bootloader that hands control to the `boot/grub.cfg` shipped for each board. The AYANEO Pocket S target currently lacks an Android bootloader (ABL), so it cannot boot even though the image staging steps are set up here.

## Layout

### Kernel configuration & firmware
- `linux_sm8550-defconfig.config` is the defconfig for the Linux 7.2.9 kernel (built with GCC 16).
- `linux_patches` holds the kernel patch series: `0000-rn72-*` are ROCKNIX's shared 7.2 msm/DPU fixes, everything else is ROCKNIX's SM8550 series (panels, rsinput + haptics rumble, ath12k, suspend, DPU rotation, ...). See "ROCKNIX alignment" below.
- `dts` holds the device trees (from ROCKNIX); `linux/linux-ext-sm8550.mk` copies them into the kernel tree before patching.
- `dracut.conf` describes the minimal initramfs: disable systemd, strip unnecessary modules, include the `busybox-rootfs` dracut module and explicitly install the Qualcomm firmware blobs (`ath12k`, `qcom`, `venus`, etc.) needed by the SoC images.
- `fsoverlay` contains the file-system overlay that ships with the initramfs (fan-daemon startup script, Bluetooth MAC derivation, udev rules for the bundled gamepads and other device-node tweaks plus the supported firmware tree).

### Board-specific artifacts
Each board directory (`ayn-sm8550`, `ayaneo-sm8550`) exposes:
1. A `create-boot-script.sh` that copies the kernel image, initramfs, modules, firmware bundle, rescue image and the board’s DTB into `REGLINUX_BINARIES_DIR/boot/boot` so that the final `reglinux.img` contains everything LinuxLoader expects.
2. `genimage.cfg`, which defines a 2 GB FAT boot partition named `REGLINUX` and a 512 MB `userdata` ext4 partition, then wraps them in an HD image that the bootloader can flash.
3. `grub.cfg`, the bootloader configuration and menu.

### Device targets
- **AYN Odin2** (and similar SM8550 units): `create-boot-script.sh` copies `qcs8550-ayn-odin2.dtb`, and the bootloader uses the stock `cmdline="clk_ignore_unused pd_ignore_unused quiet rw rootwait label=REGLINUX"`.
- **AYN Odin2 Portal**: mirrors the Odin2 flow but deploys `qcs8550-ayn-odin2portal.dtb` and adds `fbcon=rotate:3` to counter the display orientation quirks; `LinuxLoader.cfg` also keeps `Debug=true` to make troubleshooting easier.
- **AYANEO Pocket S / S Mini**: one GRUB entry per panel: `qcs8550-ayaneo-pockets2k.dtb`, `qcs8550-ayaneo-pockets1k.dtb` (WT0600 1080p panel) and `qcs8550-ayaneo-pocketsmini.dtb`. If the screen stays black, pick the other Pocket S entry.

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
- **AYANEO Pocket S / S Mini** – device trees and GRUB entries exist; the boot chain (a loader that hands over to GRUB) is still unverified on this device.

## ROCKNIX alignment (Linux 7.2, 2026-10)

The kernel, device trees, audio topology and UCM follow ROCKNIX's SM8550 tree
(github.com/ROCKNIX/distribution, `projects/ROCKNIX/devices/SM8550`), which runs
the same Mesa (26.2.4) on the same 7.2 kernel. REG-specific choices:

- GPU zap shader: `qcom/sm8550/a740_zap.mbn`, the upstream linux-firmware file
  (added 2025-12). Its code segment is byte-identical to the AYN and AYANEO
  vendor copies we used to ship under `ayn/` and `ayaneo/`, and all three are
  signed by the same Qualcomm generic test root, so one file serves every device.
- Fan: the device trees have no thermal cooling maps; `qcom-fan` (S06qcom-fan)
  is the only thing that drives `pwm1`. Before 7.2 the kernel thermal maps and
  the daemon both wrote it.
- AYANEO pads: `S11ayaneo-gamepad` sends ROCKNIX's serial frame on `/dev/ttyHS0`
  to put the MCU in Xbox 360 mode (045e:028e), and the cmdline sets that device
  to 2 ms USB polling (`usbcore.interrupt_interval_override`, patch 0506).
- UCM: ucm.conf only matches `conf.d/<driver>/<card long name>.conf`, and under
  our EFI boot the long name comes from DMI (`ayaneo-AYANEOPocketACE-` style).
  - Odin 2 / Mini / Portal: AYN's vendor config (`ayn-alsa-ucm-conf`, same
    author as ROCKNIX's, newer, with the headset mic that ROCKNIX comments out).
    AYN's kernel names the card `SM8550-AYN`; the package links our `AYN-Odin2`
    card and its EFI long names to it, and installs only AYN's own files (the
    repository is a full, older alsa-ucm-conf fork).
  - Thor and AYANEO Pockets: ROCKNIX's configs (`patches/alsa-ucm-conf/0004`-`0009`);
    the Thor one adds the internal DMIC and amp settings.
  - `0010` and the Portal/Mini links are our best guess at the EFI long names:
    check `/proc/asound/cards` on the device and fix them if they differ.

### DRIVER_SYNCOBJ_TIMELINE (old patch 0070, dropped)

We used to carry `0070-drm-msm-remove-DRIVER_SYNCOBJ_TIMELINE.patch` (Philippe
Simons, Sept 2025, taken from ROCKNIX), which hid timeline syncobjs from
userspace again after upstream exposed them.

- Upstream: Rob Clark, "drm/msm: Expose DRIVER_SYNCOBJ_TIMELINE" (Feb 2025).
  The flag had been held back because older turnip hung on timeline
  semaphores with a non-zero point. Mesa fixed it in MR 25981 ("turnip: Fix
  timeline semaphore support", merged 2023-11-02, Mesa 23.3, also backported).
- ROCKNIX dropped the patch on 2026-05-06 (commit 3b9c0b5e7d, PR 2674); no
  reason is given for adding or dropping it.
- We ship Mesa 26.2.4, and sm8250/sm6115 never carried it.

The flag also makes `DRM_CAP_SYNCOBJ_TIMELINE` true, which lets wlroots/sway
use explicit sync (linux-drm-syncobj-v1). If sway or a Vulkan client freezes,
stutters or flickers on SM8550, first try disabling explicit sync in sway with
`WLR_RENDER_NO_EXPLICIT_SYNC=1`, before bringing the kernel patch back.

### Not taken from ROCKNIX

- GPU capped at 680 MHz unless "overclock" is enabled (1 GHz): policy choice.
- `096-cpuidle` (disables cpuidle state1 on cpu0): no rationale published.
- Suspend off by default, InputPlumber (virtual DualSense), gamepadcalibration,
  rocknix-abl, `rocknix-u-boot-dt-id` DT properties.
- Their 10 Mesa patches (rotated blits / pre-rotated WSI) and the "scanout
  offload" scripts around them: declined, we do not patch Mesa for this. The
  DPU rotation/QSEED kernel patches (rn72-0013, 0066, 0067) stay; they are
  inert unless a compositor asks the display engine to rotate or scale.
