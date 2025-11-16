# Mediatek MT8395 Board Support

This directory provides the board-specific artifacts that REG-Linux uses to build the image for the Mediatek MT8395-based Radxa NIO 12L platform.

## Layout
- `fsoverlay/lib/firmware/mediatek/…`: the firmware overlay that will be merged into `/lib/firmware`. It contains the binary blobs needed by the wireless and Bluetooth cores (MT7961, MT7668, MT8183/88/95) and is staged under `lib/firmware/mediatek` so it can be copied verbatim into buildroot artifacts.
- `linux-defconfig.config`: the kernel defconfig generated for `aarch64` Linux 6.15.0-rc2. This is the baseline configuration that the build system applies before applying Mediatek-specific patches and drivers on top of the stock kernel sources.
- `linux_patches/000-REGLINUX-Radxa-NIO12L-Audio-Support-WIP.patch`: a DTS delta that wires an HDMI DAI link into `mt8395-radxa-nio-12l.dts`, enabling HDMI audio output alongside the existing `ETDM3` link.
- `patches/alsa-ucm-conf/001-wip-mt8395-evk-sof.patch`: adds an SOF-specific UCM2 configuration for the MediaTek EVK. It brings HDMI and headphone use case files (`ucm2/MediaTek/sof-mt8395-evk` and `ucm2/conf.d/sof-mt8395-evk`) so newer SOF-enabled kernels can select the proper controls and jack handling.
- `radxa-nio-12l/`: the packaging assets for the Radxa NIO 12L board.
  - `boot/grub/grub.cfg` (EFI boot entry pointing at `/boot/linux` and `/boot/initrd.lz4`) and the saved device tree blob (`mt8395-radxa-nio-12l.dtb` in the broader build artifacts).
  - `bootloader/`: prebuilt bootloader binaries (`lk.bin` and the various `fip-*.img` images for the different eMMC/NAND variants) that need to land on the flashed storage.
  - `create-boot-script.sh`: shell helper the build system invokes to stage the final `/boot` contents, the firmware update blobs, and to copy over bootloader artifacts from this directory into `REGLINUX_BINARIES_DIR`.
  - `genimage.cfg`: the `genimage` layout used by the release. It creates a GPT image (`reglinux.img`) with a 2 GiB FAT32 `boot.vfat` partition (label `REGLINUX`) and a 256 MiB ext4 `userdata` partition (label `SHARE`). The `boot.vfat` partition is populated with the common boot files defined by `create-boot-script.sh`.

## Integration notes
- During a build, REG-Linux runs `create-boot-script.sh` to copy the kernel image, initramfs (`rootfs.cpio.lz4`), `rootfs.squashfs`, module/FW/rescue update blobs, EFI binaries, and board-specific device tree into the `REGLINUX_BINARIES_DIR`. It also stages the bootloader artifacts into `bootloader/`.
- `genimage.cfg` expects the staged tree to be mounted at `TARGET_DIR` so `boot.vfat` and `userdata.ext4` can pull the right files; hooking this board into the build involves ensuring the `radxa-nio-12l` directory is referenced by the board configuration.
- The patches under `linux_patches/` and `patches/alsa-ucm-conf/` are applied on top of the kernel and ALSA UCM sources, respectively. Keep their metadata in sync with the upstream kernel/ucm branches if you rebase or refresh audio support.

## Maintainer hints
- Update the firmware blobs in `fsoverlay/lib/firmware/mediatek/` only when Mediatek publishes new releases or when a driver requires different firmware versions.
- If you need to tweak bootloader images (`lk.bin`, `fip-*.img`), replace the files in `radxa-nio-12l/bootloader` and rerun the flashing scripts so the new binaries are packaged with any engraved release.
