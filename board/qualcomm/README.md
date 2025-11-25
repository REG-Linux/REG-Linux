# Qualcomm Board Support

This folder gathers the Qualcomm-specific artifacts that REG-Linux needs to produce bootable images for the handhelds we ship. Each numbered subdirectory schools a particular SoC family; `sm8250` and `sm8550` already document their structure and workflows, while other directories (e.g., `sdm845`, `sm6115`) currently lack dedicated README guides.

## sm8250 – Retroid Pocket family

`sm8250/` holds the shared dracut setup, firmware list, kernel defconfig, and kernel patch series that are common to RP5, Flip2, and Mini. Key files and directories include:

- `dracut.conf`: minimal initramfs definition that disables systemd support, limits modules, and explicitly installs the Qualcomm/ath11k/RTL firmware blobs listed in `kernel-firmware.txt`.
- `fsoverlay/`: overlay content shipped with the initramfs; it brings up the Qualcomm fan daemon, generates deterministic Bluetooth MACs, and exposes the bundled gamepad/haptic nodes via udev rules.
- `kernel-firmware.txt`: enumerates the Adreno 650, SM8250 subsystem, VPU, ath11k Wi-Fi, QCA Bluetooth, and RTL firmware blobs that must be packaged for the kernel and dracut.
- `linux_sm8250-defconfig.config` + `linux_patches/`: the defconfig base plus the ordered kernel patches (DTS entries, power/audio/GPU fixes, etc.) that you must keep synchronized with whatever kernel tree you build.
- `patches/`: package-level patches such as the ALSA name hints, updated UCM profiles, GroovyMAME tweaks, PipeWire buffer settings, and Vita3K hash compat fixes.

Under the board-specific subdirectories (`rp5/`, `rpflip2/`, `rpmini/`), each variant exposes:

1. `create-boot-script.sh`: invoked by the build toolchain to copy `Image`, `rootfs.cpio.lz4`, `reglinux.update`, modules/firmware/rescue updates, and the board’s DTB into `boot/boot/`, plus the `grub.cfg` and EFI payload that the device expects.
2. `genimage.cfg`: defines a 2 GiB `boot.vfat` partition (label `REGLINUX`) and a 512 MiB `userdata.ext4` partition (label `SHARE`), then concatenates them into `reglinux.img`.
3. `grub.cfg`: a zero-timeout GRUB menu that launches REGLinux with the right kernel command line (e.g., `fbcon=rotate:3` for portrait models, `console=ttyMSM0`, `clk_ignore_unused`, `pd_ignore_unused`, etc.) and board-specific DTBs.

Build/update steps documented in this directory:

1. Rebuild the SM8250 kernel from `linux_sm8250-defconfig.config` plus `linux_patches/`, ensuring any DTS patches stay in sync with the expected DTB names.
2. Produce the rootfs, modules, firmware bundles, and `rescue` image; place them in the standard `BINARIES_DIR`.
3. Run the correct board `create-boot-script.sh` so the boot tree, DTB, and EFI configuration are staged.
4. Use `genimage` with the board’s `genimage.cfg` to emit `reglinux.img` that concatenates the boot FAT and userdata ext4 partitions.

Contributor notes: keep `dracut.conf`, `kernel-firmware.txt`, and any firmware/package patches aligned with the shipped artifacts, prefer applying kernel fixes through `linux_patches/`, and update the board’s `grub.cfg`/`create-boot-script.sh` pair whenever kernel cmdlines, DTB names, or EFI layouts change.

## sm8550 – AYN Odin2, Odin2 Portal, and future AYANEO Pocket S

`sm8550/` documents the LinuxLoader-based workflow for Odin2, Odyssey Portal, and the AYANEO Pocket S (the Pocket S is still unbootable because it currently lacks an Android bootloader). This directory bundles the kernel defconfig, patch series, dracut configuration, firmware overlay, and package patches that underlie those builds.

Shared contents:

- `linux_sm8550-defconfig.config`: the 6.12.1-based starting point for the SM8550 kernel.
- `linux_patches/`: enables vendor peripherals (panels, GPU, MMC, USB/PHY, regulators, LEDs/RTC, DTB entries, QoS fixes, etc.); apply these patches in order.
- `dracut.conf`: minimal initramfs configuration that strips systemd, installs the `busybox-rootfs` module, and explicitly pulls Qualcomm firmware blobs such as `ath12k`, `qcom`, and `venus-*`.
- `fsoverlay/`: overlays the fan daemon, Bluetooth MAC tooling, udev rules for gamepads, and firmware directories needed at runtime.
- `patches/`: includes package tweaks (`alsa-lib`, `alsa-ucm-conf`, `pipewire`, `groovymame`, `vita3k`) required by the handhelds’ audio stack and emulation software.

Each board-specific directory (`odin2/`, `odin2portal/`, `pockets/`) provides:

1. `create-boot-script.sh`: copies the kernel, initramfs, modules, firmware, rescue, and board DTB into `REGLINUX_BINARIES_DIR/boot/boot`, ensuring LinuxLoader sees the expected files.
2. `genimage.cfg`: describes a 2 GiB FAT boot partition labeled `REGLINUX` and a 512 MiB `userdata` partition, then wraps them in an HD image.
3. `LinuxLoader.cfg`: the LinuxLoader configuration that points to the staged kernel/initrd/DTB, sets options such as `DisableDisplayHW`, `Target=Linux`, USB host mode, and adjusts volume-button behavior.

Device-specific notes:

- **AYN Odin2**: boots with `qcs8550-ayn-odin2.dtb` and the stock `cmdline="clk_ignore_unused pd_ignore_unused quiet rw rootwait label=REGLINUX"`.
- **AYN Odin2 Portal**: reuses the Odin2 flow but stages `qcs8550-ayn-odin2portal.dtb`, enables `fbcon=rotate:3`, and keeps `Debug=true` in `LinuxLoader.cfg`.
- **AYANEO Pocket S**: expects `sm8550-ayaneo-ps.dtb`; scripts are ready but the device lacks a usable Android bootloader (ABL), so it cannot boot today.

Build/staging procedure:

1. Start from `linux_sm8550-defconfig.config`, apply the ordered patches under `linux_patches/`, and build the kernel plus all board DTBs.
2. Assemble the rootfs/rescue images; dracut reads `dracut.conf` and includes the `fsoverlay/` content.
3. Run a board’s `create-boot-script.sh` so `boot/boot/` receives `linux`, `initrd.lz4`, module/firmware/rescue updates, and the board DTB.
4. Run `genimage` with that board’s `genimage.cfg` to produce `reglinux.img`.
5. Flash the custom LinuxLoader (via vendor tooling) since these images are LinuxLoader-only. Each `LinuxLoader.cfg` already targets Linux, toggles display/USB options, and points to the staged payload.

Additional notes:

- The `fsoverlay/etc/init.d` scripts handle fan control and Bluetooth MAC generation, while `udev/rules.d`/`usr/lib/udev/rules.d` ensure attached controllers register as joysticks.
- Keep the firmware entries installed by `dracut.conf` synchronized with the firmware tree you ship (the list already covers `ath12k`, `qcom`, `venus-*`, etc.).
- Status: Odin2 and Odin2 Portal are supported; the AYANEO Pocket S build exists but is unbootable until a usable ABL is available.

## Other directories

- `sdm845/` and `sm6115/` exist under this tree but do not yet have dedicated README documentation. Inspect their contents directly when you need to understand their workflow.
